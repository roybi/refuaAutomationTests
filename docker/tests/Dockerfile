# syntax=docker/dockerfile:1
# refuaAutomationTests as a backend service: web UI + REST API that start run_tests.py,
# keep every run's results and Allure report on the /data volume and serve them.
#
#   docker build -f docker/tests/Dockerfile --build-arg CORE_IMAGE=<registry>/refua-automation-core:<tag> -t refua-automation-tests .
#
# Secrets (.env.test content: AUTOMATION_SECRET, ORM_DB_*, ...) are NEVER baked into the image;
# inject them as environment variables (the suite loads .env.<env> with override=False, so env vars win).

ARG CORE_IMAGE=refua-automation-core:latest
FROM ${CORE_IMAGE}

ARG ALLURE_VERSION=2.30.0
ARG APP_VERSION=dev
ARG GIT_SHA=unknown

ENV PYTHONPATH=/app \
    DATA_DIR=/data \
    ALLURE_BIN=/opt/allure/bin/allure \
    TEST_ENV=test \
    SERVICE_PORT=8080

# Java runs the Allure CLI; the CLI is verified against its published checksum.
USER root
RUN apt-get update \
 && apt-get install -y --no-install-recommends openjdk-17-jre-headless ca-certificates curl \
 && rm -rf /var/lib/apt/lists/* \
 && base="https://repo.maven.apache.org/maven2/io/qameta/allure/allure-commandline/${ALLURE_VERSION}" \
 && curl -fsSL "${base}/allure-commandline-${ALLURE_VERSION}.tgz" -o /tmp/allure.tgz \
 && echo "$(curl -fsSL "${base}/allure-commandline-${ALLURE_VERSION}.tgz.sha1")  /tmp/allure.tgz" | sha1sum -c - \
 && mkdir -p /opt/allure \
 && tar -xzf /tmp/allure.tgz -C /opt/allure --strip-components=1 \
 && rm /tmp/allure.tgz \
 && /opt/allure/bin/allure --version

WORKDIR /app
COPY requirements.txt requirements-service.txt ./
RUN pip install -r requirements.txt -r requirements-service.txt

COPY run_tests.py conftest.py pytest.ini ./
COPY refua_tests ./refua_tests
COPY refua_service ./refua_service
COPY tools ./tools

# /data is the persistent volume: run metadata, logs, Allure results + reports, DB-seed manifests, HOME of the test process.
RUN mkdir -p /data && chown -R pwuser:pwuser /data /app
USER pwuser
VOLUME ["/data"]
EXPOSE 8080

LABEL org.opencontainers.image.title="refua-automation-tests" \
      org.opencontainers.image.description="Refua test automation backend (runner API + UI + Allure reports)" \
      org.opencontainers.image.version="${APP_VERSION}" \
      org.opencontainers.image.revision="${GIT_SHA}"

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD curl -fsS "http://127.0.0.1:${SERVICE_PORT}/api/health" || exit 1

# One worker on purpose: the run queue and the child processes live in this process.
CMD ["sh", "-c", "exec uvicorn refua_service.app:app --host 0.0.0.0 --port ${SERVICE_PORT} --workers 1"]
