FROM python:3.12-slim

WORKDIR /app
COPY trainerize_performance/requirements.txt /app/trainerize_performance/requirements.txt
RUN pip install --no-cache-dir -r /app/trainerize_performance/requirements.txt

COPY trainerize_performance /app/trainerize_performance
COPY reporting_control /app/reporting_control
COPY scripts/trainerize_performance_reporting.py /app/scripts/trainerize_performance_reporting.py
COPY scripts/trainerize_client.py /app/scripts/trainerize_client.py

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "4", "--timeout", "300", "trainerize_performance.app:app"]
