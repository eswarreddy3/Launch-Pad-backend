#!/usr/bin/env bash
# =============================================================================
# db.sh — MySQL database management + Django migrations
# Usage: bash scripts/db.sh <command>
#
# Commands:
#   create    Create the MySQL database and user
#   drop      Drop the database (destructive!)
#   reset     Drop + recreate + migrate (destructive!)
#   migrate   Run Django migrations
#   makemigrations  Make Django migrations
#   shell     Open Django shell
# =============================================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
ENV_FILE="$BACKEND_DIR/.env"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()    { echo -e "${GREEN}[db]${NC} $*"; }
warning() { echo -e "${YELLOW}[db]${NC} $*"; }
error()   { echo -e "${RED}[db]${NC} $*"; exit 1; }

# Load .env variables
if [ -f "$ENV_FILE" ]; then
  set -a
  source "$ENV_FILE"
  set +a
else
  error "backend/.env not found. Run 'bash scripts/setup.sh' first."
fi

DB_NAME="${DB_NAME:-fynity_db}"
DB_USER="${DB_USER:-fynity_user}"
DB_PASSWORD="${DB_PASSWORD:-}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-3306}"

# Activate Python venv
activate_venv() {
  if [ -f "$BACKEND_DIR/.venv/bin/activate" ]; then
    source "$BACKEND_DIR/.venv/bin/activate"
  elif [ -f "$BACKEND_DIR/.venv/Scripts/activate" ]; then
    source "$BACKEND_DIR/.venv/Scripts/activate"
  else
    error "Virtual environment not found. Run 'bash scripts/setup.sh' first."
  fi
}

mysql_exec() {
  mysql -h "$DB_HOST" -P "$DB_PORT" -u root -p "$@"
}

cmd="${1:-help}"

case "$cmd" in
  create)
    info "Creating database '$DB_NAME' and user '$DB_USER'..."
    mysql_exec <<EOF
CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${DB_USER}'@'${DB_HOST}' IDENTIFIED BY '${DB_PASSWORD}';
GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '${DB_USER}'@'${DB_HOST}';
FLUSH PRIVILEGES;
EOF
    info "Database created. Running initial migrations..."
    activate_venv
    cd "$BACKEND_DIR"
    DJANGO_SETTINGS_MODULE=config.settings.local python manage.py migrate
    info "Done."
    ;;

  drop)
    warning "This will permanently drop database '$DB_NAME'."
    read -rp "Type 'yes' to confirm: " confirm
    [ "$confirm" = "yes" ] || { info "Aborted."; exit 0; }
    mysql_exec <<EOF
DROP DATABASE IF EXISTS \`${DB_NAME}\`;
DROP USER IF EXISTS '${DB_USER}'@'${DB_HOST}';
FLUSH PRIVILEGES;
EOF
    info "Database dropped."
    ;;

  reset)
    warning "This will DROP and recreate '$DB_NAME'. All data will be lost."
    read -rp "Type 'yes' to confirm: " confirm
    [ "$confirm" = "yes" ] || { info "Aborted."; exit 0; }
    bash "$0" drop <<< "yes"
    bash "$0" create
    ;;

  migrate)
    activate_venv
    cd "$BACKEND_DIR"
    info "Running migrations..."
    DJANGO_SETTINGS_MODULE=config.settings.local python manage.py migrate "${@:2}"
    info "Migrations complete."
    ;;

  makemigrations)
    activate_venv
    cd "$BACKEND_DIR"
    info "Making migrations..."
    DJANGO_SETTINGS_MODULE=config.settings.local python manage.py makemigrations "${@:2}"
    ;;

  shell)
    activate_venv
    cd "$BACKEND_DIR"
    DJANGO_SETTINGS_MODULE=config.settings.local python manage.py shell
    ;;

  *)
    echo "Usage: bash scripts/db.sh <command>"
    echo ""
    echo "Commands:"
    echo "  create          Create MySQL DB + user, run initial migrations"
    echo "  drop            Drop the database and user (destructive!)"
    echo "  reset           Drop + recreate + migrate (destructive!)"
    echo "  migrate         Run Django migrations"
    echo "  makemigrations  Make new Django migrations"
    echo "  shell           Open Django shell"
    ;;
esac
