#!/bin/bash
set -e

echo "=========================================="
echo "  Rare Disease Genetic Diagnosis System"
echo "=========================================="

# Create necessary directories
mkdir -p /app/data /app/logs /var/log/supervisor /var/log/nginx

# Set default environment variables
export DATABASE_URL="${DATABASE_URL:-sqlite:////app/data/rare_disease_diagnosis.db}"
export LOG_LEVEL="${LOG_LEVEL:-INFO}"
# Inside the container 0.0.0.0 is correct and required: the container
# boundary is what limits exposure, and `docker run -p` cannot reach a
# process bound to the container's loopback. Host-level defaults are
# loopback instead — see modules/RareSystem/backend/main.py.
export API_HOST="${API_HOST:-0.0.0.0}"
export API_PORT="${API_PORT:-8000}"

# Initialize database
echo "Initializing database..."
cd /app/backend
python -c "
import os
import sys
sys.path.insert(0, '/app')

# Ensure data directory exists
os.makedirs('/app/data', exist_ok=True)

import database.models
import database.case_models
from database.session import init_db
init_db()
print('Database initialized successfully')
"

cd /app

# Set permissions (appuser created in Dockerfile)
chown -R appuser:appuser /app/data /app/logs 2>/dev/null || true

echo "Starting services..."
echo "  - Backend API: http://localhost:8000"
echo "  - Frontend: http://localhost:8181"
echo ""

# Start supervisor
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
