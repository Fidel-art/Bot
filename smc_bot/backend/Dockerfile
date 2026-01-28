# Backend API Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . /app/backend/

# Copy database module
COPY ../database /app/database/

# Create necessary directories
RUN mkdir -p /app/data /app/logs

# Expose port
EXPOSE 8000

# Set Python path
ENV PYTHONPATH=/app

# Run the application
CMD ["uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
