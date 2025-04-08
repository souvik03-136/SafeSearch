#!/usr/bin/env bash
set -euo pipefail

# Load environment
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# Configuration
HOST_CSV_PATH="./data/crimes.csv"
CONTAINER_CSV_PATH="/data/crimes.csv"
DB_SERVICE="db"
DB_USER="${POSTGRES_USER:-user}"
DB_NAME="${POSTGRES_DB:-searchdb}"
DB_TIMEOUT=30  # seconds

usage() {
  cat <<EOF
Usage: $0 [command]

Commands:
  init      Initialize database and import data
  up        Build and start all services
  clean     Remove all containers and volumes
  help      Show this help

Environment:
  .env file is required with proper PostgreSQL credentials
  CSV file must exist at $HOST_CSV_PATH

EOF
  exit 1
}

check_csv() {
  if [ ! -f "$HOST_CSV_PATH" ]; then
    echo "ERROR: CSV file not found at $HOST_CSV_PATH"
    echo "       Please ensure the file exists in the data directory"
    exit 1
  fi
}

wait_for_db() {
  local count=0
  echo -n "🔄 Waiting for database (timeout: ${DB_TIMEOUT}s)..."
  until docker-compose exec -T "$DB_SERVICE" \
    psql -U "$DB_USER" -d "$DB_NAME" -c '\q' >/dev/null 2>&1; 
  do
    sleep 1
    count=$((count+1))
    if [ $count -ge $DB_TIMEOUT ]; then
      echo -e "\n❌ ERROR: Database connection timeout"
      exit 1
    fi
    echo -n "."
  done
  echo -e "\n✅ Database connection established"
}

case "${1-}" in
  init)
    check_csv
    echo "⏳ Initializing database..."
    docker-compose up -d "$DB_SERVICE"
    
    wait_for_db

    echo "📄 Applying database schema..."
    if [ -f init.sql ]; then
      docker-compose exec -T "$DB_SERVICE" \
        psql -U "$DB_USER" -d "$DB_NAME" -f init.sql
      echo "✅ Schema applied"
    else
      echo "⚠️  Warning: No init.sql found - using existing schema"
    fi

    echo "📥 Importing data from CSV..."
    export PGPASSWORD="${POSTGRES_PASSWORD}"
    docker-compose exec -T "$DB_SERVICE" \
      psql -U "$DB_USER" -d "$DB_NAME" \
      -c "\COPY crimes FROM '$CONTAINER_CSV_PATH' WITH (FORMAT csv, HEADER true)"
    unset PGPASSWORD
    
    echo "🎉 Database initialization complete!"
    ;;

  up)
    check_csv
    echo "⚙️  Building and starting all services..."
    docker-compose up --build
    ;;

  clean)
    echo "🧹 Removing all containers and volumes..."
    docker-compose down -v
    ;;

  help|--help|-h)
    usage
    ;;

  *)
    if [ -z "${1-}" ]; then
      echo "ℹ️  No command specified - starting services..."
      docker-compose up --build
    else
      echo "❌ Unknown command: $1"
      usage
    fi
    ;;
esac