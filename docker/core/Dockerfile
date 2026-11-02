# syntax=docker/dockerfile:1
# Base image: refuaAutomationCore + Playwright (browsers and OS libraries).
# Build context = a checkout of refuaAutomationCore (see docs/guides/DOCKER_PIPELINE.md):
#   docker build -f docker/core/Dockerfile -t refua-automation-core ../refuaAutomationCore
# refuaAutomationTests builds FROM this image (docker/tests/Dockerfile).

# Default = Microsoft's public Playwright image (Python + Chromium + OS libs). To use a mirror (e.g. Nexus) later,
# pass --build-arg BASE_IMAGE=<registry>/<repo>/playwright/python:v1.56.0-noble
ARG PLAYWRIGHT_VERSION=1.56.0
ARG BASE_IMAGE=mcr.microsoft.com/playwright/python:v${PLAYWRIGHT_VERSION}-noble
FROM ${BASE_IMAGE}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /opt/refua-core
COPY setup.py README.md requirements.txt ./
COPY refua_core ./refua_core
COPY scripts ./scripts

# Editable on purpose: setup.py declares no package_data, so a regular install would drop
# refua_core/config/devices.json. The "db" extra brings psycopg2 and boto3 (DB seeding, Secrets Manager).
RUN pip install --no-cache-dir -e ".[db]" \
 && python -c "from refua_core.config.environment import EnvironmentManager; import refua_core.version as v; print('refua-core', v.__version__)"

# Run as the non-root user of the Playwright image; the tests image switches back to root only to install Java/Allure.
USER pwuser
HEALTHCHECK NONE

ARG CORE_REF=unknown
LABEL org.opencontainers.image.title="refua-automation-core" \
      org.opencontainers.image.description="Refua automation framework base image (Playwright + refua_core)" \
      refua.core.ref="${CORE_REF}"
