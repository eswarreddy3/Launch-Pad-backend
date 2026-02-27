#!/usr/bin/env bash
# =============================================================================
# setup.sh — Bootstrap local development environment
# Usage: bash scripts/setup.sh
# =============================================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()    { echo -e "${GREEN}[setup]${NC} $*"; }
warning() { echo -e "${YELLOW}[setup]${NC} $*"; }

# ── Backend ──────────────────────────────────────────────────────────────────
info "Setting up Django backend..."

cd "$BACKEND_DIR"

if [ ! -d ".venv" ]; then
  info "Creating Python virtual environment..."
  python -m venv .venv
fi

info "Activating virtual environment and installing dependencies..."
source .venv/bin/activate || source .venv/Scripts/activate

pip install --upgrade pip
pip install -r requirements/local.txt

if [ ! -f ".env" ]; then
  info "Copying .env.example → .env"
  cp .env.example .env
  warning "Edit backend/.env with your database credentials before running migrations."
else
  info ".env already exists, skipping copy."
fi

# ── Frontend ─────────────────────────────────────────────────────────────────
info "Setting up Next.js frontend..."

cd "$FRONTEND_DIR"

if [ ! -f ".env.local" ]; then
  info "Copying .env.example → .env.local"
  cp .env.example .env.local
else
  info ".env.local already exists, skipping copy."
fi

if command -v bun &>/dev/null; then
  info "Installing frontend dependencies with bun..."
  bun install
elif command -v npm &>/dev/null; then
  info "Installing frontend dependencies with npm..."
  npm install
else
  warning "Neither bun nor npm found. Install Node.js and run 'npm install' in frontend/."
fi

# ── Done ─────────────────────────────────────────────────────────────────────
echo ""
info "Setup complete!"
echo ""
echo "  Next steps:"
echo "  1. Edit backend/.env with your MySQL credentials"
echo "  2. Run:  bash scripts/db.sh create"
echo "  3. Run:  bash scripts/db.sh migrate"
echo "  4. Start backend:   cd backend && source .venv/bin/activate && python manage.py runserver"
echo "  5. Start frontend:  cd frontend && npm run dev"
