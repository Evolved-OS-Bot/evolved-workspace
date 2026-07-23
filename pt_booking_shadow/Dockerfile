FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pt_booking_shadow/requirements.txt /app/pt_booking_shadow/requirements.txt
RUN pip install --no-cache-dir -r /app/pt_booking_shadow/requirements.txt

COPY pt_booking_shadow /app/pt_booking_shadow

CMD ["sh", "-c", "gunicorn --workers 1 --threads 4 --bind 0.0.0.0:${PORT:-8080} pt_booking_shadow.app:app"]
