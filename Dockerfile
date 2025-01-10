FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all Python files
COPY *.py .
COPY config.yml .

CMD ["python", "price_feed.py"] 