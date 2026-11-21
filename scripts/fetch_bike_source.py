"""Fetch and fingerprint the original UCI archive without inspecting outcome values."""

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile


SOURCE_PAGE = "https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset"
DOWNLOAD_URL = "https://archive.ics.uci.edu/static/public/275/bike%2Bsharing%2Bdataset.zip"
ARCHIVE_NAME = "bike-sharing-dataset.zip"
MEMBERS = ("Readme.txt", "hour.csv", "day.csv")
MAX_ARCHIVE_BYTES = 5_000_000
MAX_EXPANDED_BYTES = 10_000_000


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def inspect_archive(data: bytes) -> tuple[dict, dict[str, bytes]]:
    """Read file identity and CSV headers; never parse any CSV data rows."""
    with ZipFile(io.BytesIO(data)) as archive:
        entries = [entry for entry in archive.infolist() if not entry.is_dir()]
        names = [entry.filename for entry in entries]
        if len(names) != len(set(names)) or set(names) != set(MEMBERS):
            raise ValueError(f"Unexpected archive members: {names!r}")
        if sum(entry.file_size for entry in entries) > MAX_EXPANDED_BYTES:
            raise ValueError("Archive exceeds the bounded source size")
        # Read only these fixed names; archive paths are never used for extraction.
        files = {name: archive.read(name) for name in MEMBERS}
    inventory = {}
    for name, content in files.items():
        item = {"bytes": len(content), "sha256": digest(content)}
        if name.endswith(".csv"):
            with io.TextIOWrapper(io.BytesIO(content), encoding="utf-8-sig", newline="") as stream:
                item["columns"] = next(csv.reader(stream))
        inventory[name] = item
    return inventory, files


def verify_cache(raw_dir: Path, record: dict) -> None:
    """Refuse changed raw files instead of silently replacing the recorded version."""
    if record["source_page"] != SOURCE_PAGE or record["download_url"] != DOWNLOAD_URL:
        raise ValueError("Cached source does not match this acquisition recipe")
    expected = {ARCHIVE_NAME: record["archive"]["sha256"]}
    expected.update({name: record["members"][name]["sha256"] for name in MEMBERS})
    for name, expected_hash in expected.items():
        if digest((raw_dir / name).read_bytes()) != expected_hash:
            raise ValueError(f"Raw source checksum mismatch: {name}")


def fetch_source(raw_dir: Path, report_path: Path) -> tuple[dict, bool]:
    """Create one original snapshot, or verify and reuse its unchanged local cache."""
    manifest_path = raw_dir / "source.json"
    downloaded = not manifest_path.exists()
    if not downloaded:
        record = json.loads(manifest_path.read_text(encoding="utf-8"))
        verify_cache(raw_dir, record)
    else:
        if raw_dir.exists() and any(raw_dir.iterdir()):
            raise ValueError("Incomplete source folder: use a new empty folder; do not overwrite evidence")
        with urlopen(DOWNLOAD_URL, timeout=30) as response:
            data = response.read(MAX_ARCHIVE_BYTES + 1)
        if len(data) > MAX_ARCHIVE_BYTES:
            raise ValueError("Download exceeds the bounded archive size")
        inventory, files = inspect_archive(data)
        record = {
            "source_page": SOURCE_PAGE,
            "download_url": DOWNLOAD_URL,
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
            "license": {"name": "CC BY 4.0", "url": "https://creativecommons.org/licenses/by/4.0/", "basis": "UCI dataset page, checked 2026-11-21"},
            "dataset_citation": "Fanaee-T, H. (2013). Bike Sharing [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5W894.",
            "fetch_script_sha256": digest(Path(__file__).read_bytes()),
            "archive": {"filename": ARCHIVE_NAME, "bytes": len(data), "sha256": digest(data)},
            "members": inventory,
            "selected_file": "hour.csv",
            "inspection_scope": "File hashes, byte sizes, CSV headers, and README; no CSV data rows or target statistics inspected",
            "raw_data_modifications": "None; extracted files retain their original bytes",
        }
        raw_dir.mkdir(parents=True, exist_ok=True)
        for name, content in {ARCHIVE_NAME: data, **files}.items():
            with (raw_dir / name).open("xb") as output:
                output.write(content)
        manifest_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    rendered = json.dumps(record, indent=2) + "\n"
    if report_path.exists():
        if report_path.read_text(encoding="utf-8") != rendered:
            raise ValueError("Report differs from the original source record; preserve it and choose a new path")
    else:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered, encoding="utf-8")
    return record, downloaded


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw/bike-sharing"))
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    record, downloaded = fetch_source(args.raw_dir, args.report)
    print(json.dumps({"action": "downloaded" if downloaded else "verified_cached", "archive_sha256": record["archive"]["sha256"], "members": list(record["members"]), "report": args.report.as_posix()}, indent=2))
