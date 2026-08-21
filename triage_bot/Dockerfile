FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

COPY triage_bot/requirements.txt /app/triage_bot/requirements.txt
RUN pip install --no-cache-dir -r /app/triage_bot/requirements.txt

COPY triage_bot /app/triage_bot
COPY reporting_control /app/reporting_control

CMD ["python", "-m", "triage_bot.triage"]
