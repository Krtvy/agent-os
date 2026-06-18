# Rootlabs POC Portal — production container image.
#
# Build context: the portal/ directory (not the repo root).
#   docker build -t rootlabs-portal portal/
# On Fly:
#   cd portal && fly deploy   (fly reads ./Dockerfile + ./fly.toml)

FROM python:3.12-slim-bookworm

# System deps:
#   ca-certificates — outbound TLS to Supabase
#   tini            — proper PID-1 so signals reach uvicorn and zombies get reaped
# libpq ships inside psycopg[binary]; no apt install needed for it.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates tini \
    && rm -rf /var/lib/apt/lists/*

# Non-root runtime user (defense in depth).
RUN useradd --create-home --shell /bin/bash --uid 1000 portal

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Install Python deps first so this layer is cached when only app code changes.
COPY requirements.txt /app/portal/requirements.txt
RUN pip install --no-cache-dir -r /app/portal/requirements.txt

# Application code.
COPY . /app/portal/

# /app/_private is the Fly volume mount target (portal_users.json,
# trackers_data/, poc_targets.json). Pre-create so the volume can be
# empty on first deploy.
RUN mkdir -p /app/_private \
    && chown -R portal:portal /app

USER portal

EXPOSE 8080

# tini as PID 1; uvicorn with 1 worker (keeps the Supabase pool predictable
# at 10 connections — safe on shared infra). --proxy-headers so request.url
# reports https:// behind Fly's TLS-terminating edge.
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "-m", "uvicorn", "portal.app:app", \
     "--host", "0.0.0.0", \
     "--port", "8080", \
     "--workers", "1", \
     "--proxy-headers", \
     "--forwarded-allow-ips=*"]
