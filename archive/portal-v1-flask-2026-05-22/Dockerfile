# Rootlabs POC Self-Serve Data Portal — container image
#
# Bundles: Python 3.12 + Flask app + Anthropic Claude Code CLI.
# At runtime, bind-mount the whole observer-test repo at /repo so the
# subprocess `claude --print --agent yudhishthira` can read .claude/agents/,
# lib/yudhi-*.sh, training/queries/, etc.

FROM python:3.12-slim

# System deps + Node.js (for the claude CLI which is an npm package).
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl ca-certificates gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && npm install -g @anthropic-ai/claude-code \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Python deps
WORKDIR /app
COPY portal/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code (everything else comes from the bind-mounted /repo at runtime)
COPY portal/ ./portal/

# Yudhi expects to be invoked from the repo root so relative paths
# like `lib/yudhi-sql.sh` resolve.
ENV REPO_ROOT=/repo
ENV PYTHONPATH=/app
WORKDIR /repo

EXPOSE 5000

# gthread workers because the portal threading model spawns daemon
# threads per Yudhi task — gevent/eventlet would conflict.
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "2", \
     "--worker-class", "gthread", \
     "--threads", "4", \
     "--timeout", "180", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "portal.app:app"]
