FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

COPY operating_data_hub/requirements.txt /app/operating_data_hub/requirements.txt
RUN pip install --no-cache-dir -r /app/operating_data_hub/requirements.txt

COPY operating_data_hub /app/operating_data_hub
COPY reporting_control /app/reporting_control
COPY scripts/sheets_client.py /app/scripts/sheets_client.py
COPY scripts/update_metrics.py /app/scripts/update_metrics.py

CMD ["sh", "-c", "gunicorn --workers 1 --threads 4 --timeout 900 --bind 0.0.0.0:${PORT:-8080} operating_data_hub.app:app"]

