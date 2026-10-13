FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PRODUCT_MANAGER_DB=/data/product_manager.db \
    PRODUCT_MANAGER_HOST=0.0.0.0 \
    PRODUCT_MANAGER_PORT=8000

WORKDIR /app

RUN groupadd --system app \
    && useradd --system --gid app --home-dir /app app \
    && mkdir -p /data \
    && chown app:app /data

COPY --chown=app:app api/ ./api/
COPY --chown=app:app assets/ ./assets/
COPY --chown=app:app db/schema.sql ./db/schema.sql
COPY --chown=app:app ui/ ./ui/
COPY --chown=app:app VERSION ./VERSION

USER app

EXPOSE 8000
VOLUME ["/data"]

HEALTHCHECK --interval=5s --timeout=3s --start-period=15s --retries=3 \
    CMD python -c "from urllib.request import urlopen; urlopen('http://127.0.0.1:8000/readyz', timeout=2)" || exit 1

CMD ["python", "api/app.py"]
