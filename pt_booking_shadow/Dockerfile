FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pt_booking_shadow/requirements.txt /app/pt_booking_shadow/requirements.txt
RUN pip install --no-cache-dir -r /app/pt_booking_shadow/requirements.txt

COPY pt_booking_shadow /app/pt_booking_shadow
COPY revenue_gap_control /app/revenue_gap_control
COPY reporting_control /app/reporting_control
COPY scripts/membership_reconciliation.py /app/scripts/membership_reconciliation.py
COPY scripts/trainerize_client.py /app/scripts/trainerize_client.py
COPY scripts/sheets_client.py /app/scripts/sheets_client.py

CMD ["sh", "-c", "gunicorn --workers 1 --threads 4 --bind 0.0.0.0:${PORT:-8080} pt_booking_shadow.app:app"]
