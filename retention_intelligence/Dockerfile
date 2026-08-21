FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

COPY retention_intelligence/requirements.txt /app/retention_intelligence/requirements.txt
RUN pip install --no-cache-dir -r /app/retention_intelligence/requirements.txt

COPY retention_intelligence /app/retention_intelligence
COPY reporting_control /app/reporting_control
COPY scripts/membership_reconciliation.py /app/scripts/membership_reconciliation.py
COPY scripts/trainerize_client.py /app/scripts/trainerize_client.py

RUN mkdir -p /app/data/private/integration-reporting \
    /app/outputs/trainerize-reporting-reconciliation

CMD ["sh", "-c", "gunicorn --workers 1 --threads 4 --timeout 900 --bind 0.0.0.0:${PORT:-8080} retention_intelligence.app:app"]
