# Dockerfile for FastAPI RAG API Server
FROM python:3.10-slim as builder

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

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
COPY main.py .
COPY create_vector_store.py .
COPY iso17025.json .

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app:$PYTHONPATH

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Startup script
RUN echo '#!/bin/bash\n\
set -e\n\
echo "🚀 RAG API Server Starting..."\n\
\n\
if [ -z "${OPENAI_API_KEY}" ]; then\n\
    echo "❌ OPENAI_API_KEY not set"\n\
    exit 1\n\
fi\n\
\n\
if [ ! -d "iso17025_faiss_qwen" ]; then\n\
    echo "🔄 Creating FAISS vector store..."\n\
    python create_vector_store.py\n\
    echo "✅ Vector store created"\n\
else\n\
    echo "✅ Vector store exists"\n\
fi\n\
\n\
echo "🌐 Starting FastAPI on port 8000..."\n\
exec uvicorn main:app --host 0.0.0.0 --port 8000\n\
' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]
