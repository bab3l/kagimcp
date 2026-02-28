FROM python:3.12-slim

ARG KAGIMCP_REF=v0.1.4

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MCP_TRANSPORT=streamable-http \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8000 \
    MCP_PATH=/mcp

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir "git+https://github.com/kagisearch/kagimcp.git@${KAGIMCP_REF}"

COPY docker/run_kagimcp.py /app/run_kagimcp.py
COPY docker/healthcheck.py /app/healthcheck.py

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 CMD ["python", "/app/healthcheck.py"]

ENTRYPOINT ["python", "/app/run_kagimcp.py"]
