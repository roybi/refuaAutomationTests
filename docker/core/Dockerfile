# syntax=docker/dockerfile:1
# Base image: refuaAutomationCore + Playwright (browsers and OS libraries).
# Build context = a checkout of refuaAutomationCore (see docs/guides/DOCKER_PIPELINE.md):
#   docker build -f docker/core/Dockerfile -t refua-automation-core ../refuaAutomationCore
# refuaAutomationTests builds FROM this image (docker/tests/Dockerfile).

# BASE_IMAGE is intentionally empty until the Nexus image is chosen: any image with Python 3.9+ and Chromium
# plus its OS libraries (e.g. <nexus-host>/<repo>/playwright/python:v1.56.0-noble). The build fails without it.
ARG BASE_IMAGE=
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
RUN pip install -e ".[db]" \
 && python -c "from refua_core.config.environment import EnvironmentManager; import refua_core.version as v; print('refua-core', v.__version__)"

ARG CORE_REF=unknown
LABEL org.opencontainers.image.title="refua-automation-core" \
      org.opencontainers.image.description="Refua automation framework base image (Playwright + refua_core)" \
      refua.core.ref="${CORE_REF}"
