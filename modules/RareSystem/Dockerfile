# ============================================
# Stage 1: Frontend Build
# ============================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci --legacy-peer-deps

# Copy frontend source
COPY frontend/ ./

# Build frontend
RUN npm run build

# ============================================
# Stage 2: Backend Base
# ============================================
FROM python:3.11-slim AS backend-base

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for any potential build tools
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt || \
    pip install --no-cache-dir \
    fastapi==0.109.0 \
    uvicorn[standard]==0.27.0 \
    python-multipart==0.0.6 \
    pydantic==2.5.3 \
    pydantic-settings==2.1.0 \
    sqlalchemy==2.0.25 \
    alembic==1.13.1 \
    celery==5.3.6 \
    redis==5.0.1 \
    pysam==0.22.0 \
    numpy==1.26.3 \
    pandas==2.1.4 \
    scipy==1.12.0 \
    python-dotenv==1.0.0 \
    httpx==0.26.0 \
    aiohttp==3.9.1 \
    requests==2.31.0 \
    loguru==0.7.2 \
    python-jose[cryptography]==3.3.0 \
    passlib[bcrypt]==1.7.4 \
    reportlab==4.0.8 \
    sentence-transformers==2.3.1 \
    faiss-cpu==1.7.4

# ============================================
# Stage 3: Production Image
# ============================================
FROM python:3.11-slim AS production

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python packages from builder
COPY --from=backend-base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-base /usr/local/bin /usr/local/bin

# Copy backend application
COPY backend/ ./backend/
COPY config/ ./config/
COPY requirements.txt ./

# Copy frontend build from builder
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create app user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Create necessary directories with proper permissions
RUN mkdir -p /app/data /app/logs /var/log/supervisor /var/log/nginx && \
    chown -R appuser:appuser /app/data /app/logs && \
    chmod 755 /app/data /app/logs

# Copy nginx configuration
COPY docker/nginx.conf /etc/nginx/nginx.conf

# Copy supervisor configuration
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copy startup script
COPY docker/start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DATABASE_URL=sqlite:////app/data/rare_disease_diagnosis.db \
    API_HOST=0.0.0.0 \
    API_PORT=8000 \
    LOG_LEVEL=INFO

# Expose port (nginx serves frontend + proxies API)
EXPOSE 8181

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8181/api/health || exit 1

# Start services
CMD ["/app/start.sh"]
