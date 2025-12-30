FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
RUN chmod +x /app/docker/entrypoint.sh

EXPOSE 8000

CMD ["/app/docker/entrypoint.sh"]
