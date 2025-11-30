# Dockerfile for Streamlit RAG Frontend - Optimized with layer caching
FROM python:3.10-slim as builder

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Create and copy requirements first (to leverage Docker cache)
RUN echo 'streamlit>=1.28.0\n\
requests>=2.31.0\n\
' > requirements.txt

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

# Copy only Streamlit app
COPY app_streamlit.py .

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app:$PYTHONPATH

# API URL - MUST be set via environment variable in production
# Default for local development only
ENV API_URL=http://localhost:8000

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Streamlit configuration for production
ENV STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_RUN_ON_SAVE=false \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_CLIENT_TOOLBAR_MODE=minimal

# Start Streamlit
CMD ["streamlit", "run", "app_streamlit.py"]
