"""The first HTTP entry point; currently provides a liveness check only."""

from fastapi import FastAPI

app = FastAPI(title="ShiftWatch")


@app.get("/health")
def health() -> dict[str, str]:
    """Confirm that this application can respond to a request."""
    return {"status": "ok"}
