FROM python:3.10-slim

# Install system dependencies (basic build-essential)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Ensure the uploads directory exists and is writable by any user (HF uses user 1000)
RUN mkdir -p static/uploads && chmod -R 777 static/uploads

# Expose port 7860 (Hugging Face default port)
EXPOSE 7860

# Run using gunicorn on port 7860
CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app"]
