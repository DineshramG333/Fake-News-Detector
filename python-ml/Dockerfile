FROM python:3.11-slim

WORKDIR /app

# Install dependencies first for better Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (model.py, main.py)
COPY . .

EXPOSE 5000

# Train-on-first-run happens automatically inside model.py on import,
# and the resulting model artifact is persisted to fake_news_model.joblib.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
