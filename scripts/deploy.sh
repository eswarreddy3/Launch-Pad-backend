#!/usr/bin/env bash
# =============================================================================
# deploy.sh — Production deployment helper
# Usage: bash scripts/deploy.sh [--skip-frontend] [--skip-backend]
#
# Assumes:
#   - Server has Python venv at backend/.venv
#   - DJANGO_SETTINGS_MODULE=config.settings.production
#   - A process manager (systemd/supervisor) handles the gunicorn service
#   - SERVICE_NAME env var or argument controls which systemd service to restart
# =============================================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()    { echo -e "${GREEN}[deploy]${NC} $*"; }
warning() { echo -e "${YELLOW}[deploy]${NC} $*"; }

SKIP_FRONTEND=false
SKIP_BACKEND=false
SERVICE_NAME="${SERVICE_NAME:-fynity-backend}"

for arg in "$@"; do
  case $arg in
    --skip-frontend) SKIP_FRONTEND=true ;;
    --skip-backend)  SKIP_BACKEND=true ;;
  esac
done

# ── Backend ──────────────────────────────────────────────────────────────────
if [ "$SKIP_BACKEND" = false ]; then
  info "Deploying Django backend..."

  cd "$BACKEND_DIR"

  # Activate venv
  if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
  elif [ -f ".venv/Scripts/activate" ]; then
    source .venv/Scripts/activate
  fi

  info "Installing/upgrading Python dependencies..."
  pip install --upgrade pip
  pip install -r requirements/production.txt

  info "Running database migrations..."
  DJANGO_SETTINGS_MODULE=config.settings.production python manage.py migrate --noinput

  info "Collecting static files..."
  DJANGO_SETTINGS_MODULE=config.settings.production python manage.py collectstatic --noinput --clear

  info "Restarting backend service '$SERVICE_NAME'..."
  if command -v systemctl &>/dev/null; then
    sudo systemctl restart "$SERVICE_NAME"
    info "Service restarted."
  else
    warning "systemctl not found. Restart '$SERVICE_NAME' manually."
  fi
fi

# ── Frontend ─────────────────────────────────────────────────────────────────
if [ "$SKIP_FRONTEND" = false ]; then
  info "Deploying Next.js frontend..."

  cd "$FRONTEND_DIR"

  if command -v bun &>/dev/null; then
    bun install --frozen-lockfile
    bun run build
  else
    npm ci
    npm run build
  fi

  info "Frontend built successfully."
  info "Restart your Next.js process manager (PM2, systemd, etc.) if needed."
fi

# ── Done ─────────────────────────────────────────────────────────────────────
info "Deployment complete."
