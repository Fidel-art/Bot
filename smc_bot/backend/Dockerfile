# Backend API Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from backend directory
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend /app/backend/

# Copy database module
COPY database /app/database/

# Copy config module
COPY config /app/config/

# Copy MT5 proxy (shadows real MetaTrader5 which is Linux-incompatible)
COPY mt5_proxy /app/mt5_proxy/

# Create necessary directories
RUN mkdir -p /app/data /app/logs

# Expose port
EXPOSE 8000

# Set Python path — mt5_proxy takes priority over site-packages for MetaTrader5
ENV PYTHONPATH=/app/mt5_proxy:/app

# MT5 Bridge URL (Windows host)
ENV MT5_BRIDGE_URL=http://host.docker.internal:8765

# Run the application
CMD ["uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
