FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY price_feed.py .
COPY config.yml .

CMD ["python", "price_feed.py"] 