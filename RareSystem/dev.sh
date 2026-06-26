#!/bin/bash
# ============================================================
# Rare Disease Genetic Diagnosis System - Local Dev Startup
# Runs both backend and frontend with a single command
# ============================================================

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
VENV_DIR="$PROJECT_ROOT/venv"

BACKEND_PID=""
FRONTEND_PID=""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC}  $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

cleanup() {
    echo ""
    log_info "Shutting down..."
    [ -n "$BACKEND_PID" ]  && kill "$BACKEND_PID"  2>/dev/null && log_info "Backend stopped"
    [ -n "$FRONTEND_PID" ] && kill "$FRONTEND_PID" 2>/dev/null && log_info "Frontend stopped"
    # Kill any child processes of the backend/frontend
    [ -n "$BACKEND_PID" ]  && kill -- -"$BACKEND_PID"  2>/dev/null || true
    [ -n "$FRONTEND_PID" ] && kill -- -"$FRONTEND_PID" 2>/dev/null || true
    wait 2>/dev/null
    log_info "All services stopped. Goodbye!"
    exit 0
}

trap cleanup SIGINT SIGTERM

# ----------------------------------------------------------
# 1. Dependency checks
# ----------------------------------------------------------
check_deps() {
    log_info "Checking dependencies..."

    if ! command -v python3 &>/dev/null; then
        log_error "python3 not found. Please install Python 3.9+"
        exit 1
    fi

    if ! command -v node &>/dev/null; then
        log_error "node not found. Please install Node.js 18+"
        exit 1
    fi

    if ! command -v npm &>/dev/null; then
        log_error "npm not found. Please install npm 9+"
        exit 1
    fi

    log_info "  python3: $(python3 --version)"
    log_info "  node:    $(node --version)"
    log_info "  npm:     $(npm --version)"
}

# ----------------------------------------------------------
# 2. Python environment
# ----------------------------------------------------------
setup_python_env() {
    if command -v conda &>/dev/null; then
        CONDA_ENVS=$(conda env list --json 2>/dev/null | python3 -c "
import json, sys, os
envs = json.load(sys.stdin).get('envs', [])
for e in envs:
    name = os.path.basename(e)
    py = os.path.join(e, 'bin', 'python3')
    if os.path.isfile(py):
        ok = os.access(py, os.X_OK)
        print(f'{name}\t{py}\t{\"ok\" if ok else \"no\"}')
" 2>/dev/null)

        while IFS=$'\t' read -r env_name env_py env_ok; do
            if [ "$env_ok" = "ok" ] && "$env_py" -c "import fastapi" 2>/dev/null; then
                log_info "Using conda environment: $env_name ($env_py)"
                export PYTHON="$env_py"
                CONDA_PREFIX="$("$env_py" -c "import sys; print(sys.prefix)")"
                export PATH="$CONDA_PREFIX/bin:$PATH"
                return
            fi
        done <<< "$CONDA_ENVS"

        log_warn "conda found but no environment has fastapi installed"
    fi

    if [ ! -d "$VENV_DIR" ]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv "$VENV_DIR"
    fi

    source "$VENV_DIR/bin/activate"
    log_info "Virtual environment activated: $VENV_DIR"

    if ! python3 -c "import fastapi" 2>/dev/null; then
        log_info "Installing Python dependencies into venv..."
        pip install -r "$PROJECT_ROOT/requirements.txt" -q
    fi
}

# ----------------------------------------------------------
# 3. Environment config
# ----------------------------------------------------------
# Load backend/.env into shell environment so that:
#   - check_microservice uses the real configured URLs
#   - Python subprocess inherits the correct env vars
load_backend_env() {
    local env_file="$BACKEND_DIR/.env"
    if [ -f "$env_file" ]; then
        log_info "Loading environment from $env_file"
        set -a
        source "$env_file"
        set +a
    else
        log_warn "backend/.env not found, using default values"
    fi
}

setup_env() {
    if [ ! -f "$BACKEND_DIR/.env" ]; then
        if [ -f "$BACKEND_DIR/.env.example" ]; then
            log_info "Copying backend/.env.example -> backend/.env"
            cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
        else
            log_warn "No backend/.env.example found. Creating minimal .env"
            cat > "$BACKEND_DIR/.env" << 'ENVEOF'
DATABASE_URL=sqlite:///./rare_disease_diagnosis.db
API_PORT=18000
CORS_ORIGINS=http://localhost:8888,http://127.0.0.1:8888,http://localhost:18000,http://127.0.0.1:18000
LOG_LEVEL=INFO
ENVEOF
        fi
        log_warn "Review backend/.env and configure external service URLs and API keys"
    fi

    if [ ! -f "$FRONTEND_DIR/.env" ]; then
        if [ -f "$FRONTEND_DIR/.env.example" ]; then
            log_info "Copying frontend/.env.example -> frontend/.env"
            cp "$FRONTEND_DIR/.env.example" "$FRONTEND_DIR/.env"
        else
            echo 'VITE_API_BASE_URL=http://localhost:18000/api' > "$FRONTEND_DIR/.env"
        fi
    fi
}

# ----------------------------------------------------------
# 4. Initialize database
# ----------------------------------------------------------
init_db() {
    log_info "Initializing database..."
    mkdir -p "$PROJECT_ROOT/data"
    cd "$BACKEND_DIR"
    python3 -c "
import sys, os
sys.path.insert(0, '$BACKEND_DIR')
os.makedirs('$PROJECT_ROOT/data', exist_ok=True)
from database.session import init_db
init_db()
print('Database initialized')
" 2>&1 || log_warn "Database init had issues (may already exist)"
    cd "$PROJECT_ROOT"
}

# ----------------------------------------------------------
# 5. Start backend
# ----------------------------------------------------------
start_backend() {
    log_info "Starting backend on http://localhost:18000 ..."
    cd "$BACKEND_DIR"
    export PYTHONPATH="$BACKEND_DIR"
    python3 run.py &
    BACKEND_PID=$!
    cd "$PROJECT_ROOT"
    log_info "Backend PID: $BACKEND_PID"
}

# ----------------------------------------------------------
# 6. Start frontend
# ----------------------------------------------------------
start_frontend() {
    log_info "Starting frontend on http://localhost:8888 ..."
    cd "$FRONTEND_DIR"
    npm run dev &
    FRONTEND_PID=$!
    cd "$PROJECT_ROOT"
    log_info "Frontend PID: $FRONTEND_PID"
}

# ----------------------------------------------------------
# 7. Wait for services + status display
# ----------------------------------------------------------
wait_for_services() {
    echo ""
    echo -e "${CYAN}============================================${NC}"
    echo -e "${CYAN}  Rare Disease Genetic Diagnosis System${NC}"
    echo -e "${CYAN}============================================${NC}"
    echo ""
    log_info "Frontend:  http://localhost:8888"
    log_info "Backend:   http://localhost:18000"
    log_info "API Docs:  http://localhost:18000/docs"
    log_info "Health:    http://localhost:18000/api/health"
    echo ""

    # Check external microservice connectivity
    check_microservice "VEP"          "${VEP_API_BASE_URL}"
    check_microservice "HPO"          "${HPO_API_BASE_URL}"
    check_microservice "Phenotype-HPO" "${PHENOTYPE_HPO_API_BASE_URL}"
    check_microservice "PPI Score"    "${PPI_SCORE_API_BASE_URL}"
    check_microservice "Ranking"       "${RANK_API_BASE_URL}"
    check_microservice "Report"       "${REPORT_API_BASE_URL}"
    echo ""
    log_info "Press Ctrl+C to stop all services"
    echo ""

    # Wait for backend health
    log_info "Waiting for backend to be ready..."
    for i in $(seq 1 30); do
        if curl -sf http://localhost:18000/api/health >/dev/null 2>&1; then
            log_info "Backend is ready!"
            break
        fi
        if [ "$i" -eq 30 ]; then
            log_warn "Backend health check timed out (may still be starting)"
        fi
        sleep 1
    done

    wait
}

# Check if a microservice endpoint is reachable (1s timeout)
check_microservice() {
    local name="$1"
    local url="$2"
    if curl -sf --connect-timeout 1 --max-time 2 "$url" >/dev/null 2>&1; then
        log_info "  $name: reachable ($url)"
    else
        log_warn "  $name: unreachable ($url) - check $name URL in backend/.env"
    fi
}

# ============================================================
# Main
# ============================================================
echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}  Starting Development Environment...${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""

check_deps
setup_python_env
setup_env
load_backend_env
# init_db
start_backend
start_frontend
wait_for_services
