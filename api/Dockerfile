# Dockerfile for FastAPI RAG API Server - Optimized with layer caching
FROM python:3.10-slim as builder

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copy only requirements first (to leverage Docker cache)
COPY requirements.txt .

# Install dependencies in a separate layer for better caching
RUN pip install --no-cache-dir --user --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.10-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

WORKDIR /app

# Copy only necessary files for API
COPY iso17025.json .
COPY main.py .
COPY create_vector_store.py .

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app:$PYTHONPATH

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Startup script with improved logging
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "Starting RAG API Server..."\n\
\n\
if [ -z "${OPENAI_API_KEY}" ]; then\n\
    echo "ERROR: OPENAI_API_KEY environment variable not set"\n\
    exit 1\n\
fi\n\
\n\
if [ ! -d "iso17025_faiss_qwen" ]; then\n\
    echo "Creating FAISS vector store..."\n\
    python create_vector_store.py\n\
    echo "Vector store created successfully"\n\
else\n\
    echo "Vector store already exists"\n\
fi\n\
\n\
echo "Starting FastAPI server on port 8000..."\n\
exec uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1\n\
' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]
