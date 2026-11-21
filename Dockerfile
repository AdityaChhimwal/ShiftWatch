# Pin the official Python base so this recipe keeps using the same starting image.
FROM python:3.13-slim@sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d350d98134cf1070bc106ee9ed90

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --disable-pip-version-check -r requirements.txt \
    && python -m pip check

COPY src ./src
USER 10001:10001
EXPOSE 8000

CMD ["python", "-m", "uvicorn", "shiftwatch.api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
