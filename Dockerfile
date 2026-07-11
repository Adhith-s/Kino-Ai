# Use Python 3.11-slim as base
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt .

# Install CPU-only PyTorch first to significantly reduce Docker image size (saving ~1.5GB)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install the rest of the backend requirements
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the SentenceTransformer model to bake it into the image.
# This avoids slow first-load in production and bypasses any SSL verify issues on build machines.
RUN python -c "import httpx; orig = httpx.Client.__init__; httpx.Client.__init__ = lambda self, *a, **k: orig(self, *a, **{**k, 'verify': False}); from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy the rest of the application
COPY . .

# Default environment variables
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Expose the default port
EXPOSE 8000

# Start the application
# We use sh -c to support the dynamic $PORT environment variable injected by hosting platforms (e.g. Render, Cloud Run)
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}"]
