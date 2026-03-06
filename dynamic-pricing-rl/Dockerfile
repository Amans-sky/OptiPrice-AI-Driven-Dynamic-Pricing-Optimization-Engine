# Use official Python runtime as base image
FROM python:3.10-slim

# Set working directory in container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip to latest version
RUN pip install --upgrade pip

# Copy requirements file first (layer caching optimization)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create required directories
RUN mkdir -p models checkpoints data logs

# Create non-root user for security
RUN useradd -m appuser
USER appuser

# Expose ports
# FastAPI: 8000
# Streamlit: 8501
EXPOSE 8000 8501

# Health check for API
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command runs API
# Can be overridden for training (python run.py) or dashboard (streamlit run dashboard/app.py)
CMD ["uvicorn", "api.pricing_api:app", "--host", "0.0.0.0", "--port", "8000"]
