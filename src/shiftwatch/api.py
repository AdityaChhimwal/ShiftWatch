"""HTTP surface for the ShiftWatch dashboard and session API."""

from contextlib import asynccontextmanager
import csv
import gzip
import io
import json
import os
from pathlib import Path
import tempfile

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from .contracts import LabelRecord
from .drift import make_reference
from .model import ARTIFACTS, load_artifacts, predict
from .quality import ID, MAX_COUNT
from .replay import BATCHES, DURATION, LABEL_DELAY, PRE, SCENARIOS, due_labels, make_replay
from .storage import SessionError, Store

STATIC = Path(__file__).with_name("static")
MAX_ROWS = 500
MAX_BODY = 256_000
MAX_IN_FLIGHT = 2


@asynccontextmanager
async def lifespan(app):
    models, reference, policy, versions = load_artifacts()
    database = os.environ.get("SHIFTWATCH_DB", str(Path(tempfile.gettempdir()) / "shiftwatch.sqlite3"))
    app.state.store = Store(database, models["candidate"], reference, policy, versions)
    with gzip.open(ARTIFACTS / "demo.json.gz", "rt") as stream:
        app.state.examples = json.load(stream)
    app.state.in_flight = 0
    yield


app = FastAPI(title="ShiftWatch", lifespan=lifespan)
app.mount("/assets", StaticFiles(directory=STATIC), name="assets")


@app.middleware("http")
async def bound_session_work(request, call_next):
    if not request.url.path.startswith("/sessions"):
        return await call_next(request)
    if request.app.state.in_flight >= MAX_IN_FLIGHT:
        return JSONResponse({"detail": "Service busy. Retry shortly."}, status_code=503)
    request.app.state.in_flight += 1
    try:
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        return response
    finally:
        request.app.state.in_flight -= 1


@app.exception_handler(SessionError)
async def session_error(request, error):
    return JSONResponse({"detail": str(error)}, status_code=error.status)


async def payload(request: Request):
    if request.headers.get("content-type", "").split(";")[0].strip() != "application/json":
        raise HTTPException(415, "Send application/json")
    buffer = bytearray()
    async for chunk in request.stream():
        if len(buffer) + len(chunk) > MAX_BODY:
            raise HTTPException(413, "Request exceeds 256,000 bytes")
        buffer.extend(chunk)
    try:
        result = json.loads(buffer)
    except (ValueError, RecursionError):
        raise HTTPException(422, "Invalid JSON") from None
    if not isinstance(result, dict):
        raise HTTPException(422, "Expected a JSON object")
    return result


def rows_payload(data, fields):
    if set(data) != set(fields) or not isinstance(data.get("rows"), list):
        raise HTTPException(422, "Unexpected request fields or invalid rows")
    rows = data["rows"]
    if not 1 <= len(rows) <= MAX_ROWS:
        raise HTTPException(422, "Send 1 to 500 rows")
    return rows


def access_token(request):
    token = request.headers.get("Authorization", "")
    if not token.startswith("Bearer ") or len(token) != 50:
        raise HTTPException(404, "Session unavailable")
    return token[7:]


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC / "index.html")

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/scenarios")
def scenarios():
    return [{"id": key, "title": value[0]} for key, value in SCENARIOS.items()]


@app.post("/sessions", status_code=201)
def create_session(request: Request, data=Depends(payload)):
    mode = data.get("mode")
    if set(data) != {"mode"} or not isinstance(mode, str) or (mode != "custom" and mode not in SCENARIOS):
        raise HTTPException(422, "Choose custom or a supported scenario")
    return request.app.state.store.create(mode)


@app.post("/sessions/{session}/batches")
def submit_batch(session: str, request: Request, data=Depends(payload)):
    rows = rows_payload(data, ("batch_id", "rows"))
    batch = data["batch_id"]
    if not isinstance(batch, str) or not ID.fullmatch(batch):
        raise HTTPException(422, "Invalid batch_id")
    store, token = request.app.state.store, access_token(request)
    with store.transaction() as db:
        entry = store.authorize(db, session, token)
        if entry["mode"] != "custom":
            raise HTTPException(409, "Use replay steps for a demo session")
        try:
            changed = store.add_batch(db, session, batch, entry["step"], rows)
        except RecursionError:
            raise HTTPException(422, "Rows are nested too deeply") from None
        if changed:
            db.execute("UPDATE sessions SET step=step+1 WHERE id=?", (session,))
        return store.report(db, session, store.authorize(db, session, token))


@app.post("/sessions/{session}/labels")
def submit_labels(session: str, request: Request, data=Depends(payload)):
    rows = rows_payload(data, ("rows",))
    labels = {}
    for row in rows:
        try:
            label = LabelRecord.model_validate(row)
        except ValidationError:
            raise HTTPException(422, "Invalid label row. Send record_id and a nonnegative integer cnt.") from None
        if label.cnt > MAX_COUNT:
            raise HTTPException(422, "Label count exceeds the supported maximum")
        if label.record_id in labels and labels[label.record_id] != label.cnt:
            raise HTTPException(409, "Conflicting labels within request")
        labels[label.record_id] = label.cnt
    store, token = request.app.state.store, access_token(request)
    with store.transaction() as db:
        entry = store.authorize(db, session, token)
        if entry["mode"] != "custom":
            raise HTTPException(409, "Demo labels arrive through replay steps")
        added = store.add_labels(db, session, labels)
        return {**store.report(db, session, entry), "new_labels": added}


@app.post("/sessions/{session}/step")
def replay_step(session: str, request: Request, data=Depends(payload)):
    expected = data.get("step")
    if set(data) != {"step"} or type(expected) is not int or expected < 0:
        raise HTTPException(422, "Send the expected nonnegative step")
    store, token = request.app.state.store, access_token(request)
    with store.transaction() as db:
        entry = store.authorize(db, session, token)
        step, mode = entry["step"], entry["mode"]
        if mode == "custom" or expected > step:
            raise HTTPException(409, "Step unavailable")
        if expected == step < BATCHES + LABEL_DELAY:
            reference_rows, batches, _ = make_replay(request.app.state.examples, mode, 106)
            if step < BATCHES:
                inputs = [row for row, _ in reference_rows]
                reference = make_reference(inputs, predict(store.model, inputs))
                store.add_batch(db, session, str(step + 1), step, batches[step]["rows"], reference)
            source, due = due_labels(batches, step)
            if source is not None:
                ids = db.execute("SELECT id FROM predictions WHERE session=? AND batch=?",
                                 (session, str(source + 1)))
                store.add_labels(db, session, {row["id"]: due[row["id"]] for row in ids}, step)
            db.execute("UPDATE sessions SET step=step+1 WHERE id=?", (session,))
        return session_report(store, db, session, store.authorize(db, session, token))


def session_report(store, db, session, entry):
    report = store.report(db, session, entry)
    if entry["mode"] != "custom":
        report.update(total_steps=BATCHES + LABEL_DELAY, label_delay=LABEL_DELAY)
        if entry["step"] >= BATCHES + LABEL_DELAY:
            channel = SCENARIOS[entry["mode"]][1]
            report["incident"] = {"channel": channel, "first_batch": PRE + 1,
                                  "last_batch": PRE + DURATION} if channel else None
    return report


@app.get("/sessions/{session}/report")
def read_report(session: str, request: Request):
    store, token = request.app.state.store, access_token(request)
    with store.transaction(write=False) as db:
        return session_report(store, db, session, store.authorize(db, session, token))


def safe_cell(value):
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


@app.get("/sessions/{session}/export")
def export(session: str, request: Request, format: str = "json"):
    store, token = request.app.state.store, access_token(request)
    if format not in ("json", "csv"):
        raise HTTPException(422, "Choose json or csv")
    with store.transaction(write=False) as db:
        entry = store.authorize(db, session, token)
        rows = store.export_rows(db, session)
        if format == "json":
            return JSONResponse({**session_report(store, db, session, entry), "predictions": rows},
                                headers={"Content-Disposition": "attachment; filename=shiftwatch.json"})
        stream = io.StringIO(newline="")
        writer = csv.writer(stream)
        writer.writerow(("record_id", "batch_id", "event_time", "prediction", "model_version",
                         "actual", "label_received", "label_step"))
        writer.writerows([safe_cell(value) for value in row.values()] for row in rows)
        return Response(stream.getvalue(), media_type="text/csv",
                        headers={"Content-Disposition": "attachment; filename=shiftwatch.csv"})
