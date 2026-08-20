FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY cancellation_finalizer/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY cancellation_finalizer /app/cancellation_finalizer

CMD ["python", "-m", "cancellation_finalizer.app"]

