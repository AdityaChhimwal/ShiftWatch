"""Small transactional store for isolated, expiring monitoring sessions."""

from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import secrets
import sqlite3
import time

from .drift import apply_policy
from .evaluation import inspect_batch
from .quality import observed_error

MAX_BATCHES = 24
MAX_SESSIONS = 12
SESSION_TTL = 7200


class SessionError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def fingerprint(value):
    return hashlib.sha256(value.encode()).hexdigest()


def utc_now():
    return datetime.now(timezone.utc).isoformat()


class Store:
    def __init__(self, path, model, reference, policy, versions):
        self.path = path
        self.model = model
        self.reference = reference
        self.policy = policy
        self.versions = versions
        with self.transaction() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS sessions(
                    id TEXT PRIMARY KEY, token_hash TEXT NOT NULL, expires REAL NOT NULL,
                    mode TEXT NOT NULL, version TEXT NOT NULL, step INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS batches(
                    session TEXT NOT NULL REFERENCES sessions ON DELETE CASCADE,
                    id TEXT NOT NULL, step INTEGER NOT NULL, payload TEXT NOT NULL,
                    quality TEXT NOT NULL, distribution TEXT NOT NULL, created TEXT NOT NULL,
                    PRIMARY KEY(session,id), UNIQUE(session,step)
                );
                CREATE TABLE IF NOT EXISTS predictions(
                    session TEXT NOT NULL, id TEXT NOT NULL, batch TEXT NOT NULL,
                    event_time TEXT NOT NULL, prediction REAL NOT NULL, model_version TEXT NOT NULL,
                    PRIMARY KEY(session,id),
                    FOREIGN KEY(session,batch) REFERENCES batches(session,id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS labels(
                    session TEXT NOT NULL, id TEXT NOT NULL, actual INTEGER NOT NULL,
                    received TEXT NOT NULL, step INTEGER,
                    PRIMARY KEY(session,id),
                    FOREIGN KEY(session,id) REFERENCES predictions(session,id) ON DELETE CASCADE
                );
            """)

    @contextmanager
    def transaction(self, write=True):
        db = sqlite3.connect(self.path, timeout=2)
        db.row_factory = sqlite3.Row
        try:
            db.execute("PRAGMA foreign_keys=ON")
            db.execute("BEGIN IMMEDIATE" if write else "BEGIN")
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def create(self, mode):
        session, token = secrets.token_urlsafe(16), secrets.token_urlsafe(32)
        now = time.time()
        with self.transaction() as db:
            db.execute("DELETE FROM sessions WHERE expires <= ?", (now,))
            if db.execute("SELECT COUNT(*) FROM sessions").fetchone()[0] >= MAX_SESSIONS:
                raise SessionError(503, "Session capacity reached. Try again later.")
            db.execute("INSERT INTO sessions(id,token_hash,expires,mode,version) VALUES(?,?,?,?,?)",
                       (session, fingerprint(token), now + SESSION_TTL, mode, encode(self.versions)))
        return {"session_id": session, "token": token, "mode": mode, "expires_in_seconds": SESSION_TTL}

    def authorize(self, db, session, token):
        entry = db.execute("SELECT * FROM sessions WHERE id=?", (session,)).fetchone()
        if entry is None or not secrets.compare_digest(entry["token_hash"], fingerprint(token)):
            raise SessionError(404, "Session unavailable")
        if entry["expires"] <= time.time():
            raise SessionError(410, "Session expired")
        if entry["version"] != encode(self.versions):
            raise SessionError(409, "Session artifact version changed. Start a new session.")
        return entry

    def add_batch(self, db, session, batch, step, rows, reference=None):
        # Accept JSON encodings of nonfinite input for quality reporting, never for stored predictions.
        payload = fingerprint(json.dumps(rows, sort_keys=True, separators=(",", ":")))
        existing = db.execute("SELECT payload FROM batches WHERE session=? AND id=?",
                              (session, batch)).fetchone()
        if existing:
            if existing["payload"] != payload:
                raise SessionError(409, "Batch ID already has a different payload")
            return False
        if step >= MAX_BATCHES:
            raise SessionError(409, "Session batch limit reached")
        predictions, quality, stats = inspect_batch(self.model, reference or self.reference, rows)
        for record_id in predictions:
            if db.execute("SELECT 1 FROM predictions WHERE session=? AND id=?",
                          (session, record_id)).fetchone():
                raise SessionError(409, "A record ID already has a prediction in this session")
        previous = db.execute("SELECT distribution FROM batches WHERE session=? ORDER BY step DESC LIMIT 1",
                              (session,)).fetchone()
        streak = json.loads(previous[0])["streak"] if previous else {}
        distribution = apply_policy(stats, self.policy["effect"], streak)
        db.execute("INSERT INTO batches VALUES(?,?,?,?,?,?,?)",
                   (session, batch, step, payload, encode(quality),
                    encode({**distribution, "statistics": stats}), utc_now()))
        values = [(session, row["record_id"], batch, row["event_time"], predictions[row["record_id"]],
                   self.versions["model.joblib"]) for row in rows
                  if isinstance(row, dict) and isinstance(row.get("record_id"), str)
                  and row["record_id"] in predictions]
        db.executemany("INSERT INTO predictions VALUES(?,?,?,?,?,?)", values)
        return True

    def add_labels(self, db, session, labels, step=None):
        count = 0
        for record_id, actual in labels.items():
            known = db.execute("SELECT actual FROM predictions LEFT JOIN labels USING(session,id) "
                               "WHERE session=? AND id=?", (session, record_id)).fetchone()
            if known is None:
                raise SessionError(422, "Label refers to an unknown prediction")
            if known["actual"] is not None:
                if known["actual"] != actual:
                    raise SessionError(409, "Label conflicts with the saved outcome")
                continue
            db.execute("INSERT INTO labels VALUES(?,?,?,?,?)", (session, record_id, actual, utc_now(), step))
            count += 1
        return count

    def report(self, db, session, entry):
        rows = self.export_rows(db, session)
        by_batch = {}
        for row in rows:
            by_batch.setdefault(row["batch"], []).append(row)
        timeline = []
        for batch in db.execute("SELECT * FROM batches WHERE session=? ORDER BY step", (session,)):
            values = by_batch.get(batch["id"], [])
            predictions = {row["id"]: row["prediction"] for row in values}
            labels = {row["id"]: row["actual"] for row in values if row["actual"] is not None}
            received = [row["received"] for row in values if row["received"]]
            created = datetime.fromisoformat(batch["created"])
            latest = max(received, default=None)
            timeline.append({
                "batch_id": batch["id"], "step": batch["step"], "created": batch["created"],
                "quality": json.loads(batch["quality"]),
                "distribution": json.loads(batch["distribution"]),
                "performance": {**observed_error(predictions, labels, self.policy["performance_mae"]),
                                "latest_label_received": latest,
                                "latest_label_delay_seconds": (
                                    datetime.fromisoformat(latest) - created
                                ).total_seconds() if latest else None,
                                "label_step": next((row["label_step"] for row in values
                                                    if row["label_step"] is not None), None)},
            })
        return {"mode": entry["mode"], "step": entry["step"], "policy": self.policy,
                "versions": self.versions, "timeline": timeline}

    def export_rows(self, db, session):
        return [dict(row) for row in db.execute("""
            SELECT p.id, p.batch, p.event_time, p.prediction, p.model_version,
                   l.actual, l.received, l.step AS label_step
            FROM predictions p LEFT JOIN labels l USING(session,id)
            WHERE p.session=? ORDER BY p.batch,p.id
        """, (session,))]
