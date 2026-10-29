FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/app/backend
COPY pyproject.toml README.md /app/
COPY proto /app/proto
COPY scripts/generate-proto.sh scripts/clean_generated.py /app/scripts/
COPY backend /app/backend
RUN pip install --no-cache-dir . && sh scripts/generate-proto.sh && useradd --uid 10001 --create-home app
USER app
CMD ["python", "-m", "vgm.server"]
