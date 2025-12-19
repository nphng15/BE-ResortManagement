#!/bin/bash
set -e

echo "⏳ Waiting for PostgreSQL (asyncpg)..."

python - <<'PY'
import os, asyncio
import asyncpg

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/fastapi_db")
# Strip SQLAlchemy driver prefix for asyncpg direct connection
DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

async def wait_for_db():
    for i in range(60):
        try:
            conn = await asyncpg.connect(DATABASE_URL)
            await conn.close()
            print("✅ Database is available")
            return
        except Exception as exc:
            print(f"Waiting for DB ({i+1}/60): {exc}")
            await asyncio.sleep(1)
    raise SystemExit("❌ Timed out waiting for the database")

asyncio.run(wait_for_db())
PY

echo "� Checkiing database schema/migrations state..."

# Set PGPASSWORD for psql
: "${POSTGRES_PASSWORD:=}"
export PGPASSWORD="$POSTGRES_PASSWORD"

# # 1️⃣ Reset schema
# if [ -f "/code/sql/reset_schema.sql" ]; then
#     echo "Resetting schema..."
#     psql -h db -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /code/sql/reset_schema.sql || echo "psql returned non-zero exit code"
# fi

# # 2️⃣ Init tables
# if [ -f "/code/sql/init.sql" ]; then
#     echo "Initializing tables..."
#     psql -h db -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /code/sql/init.sql || echo "psql returned non-zero exit code"
# fi

# # 3️⃣ Insert sample data
# if [ -f "/code/sql/insert_data.sql" ]; then
#     echo "Inserting sample data..."
#     psql -h db -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /code/sql/insert_data.sql || echo "psql returned non-zero exit code"
# fi

# # 4️⃣ Add foreign keys
# if [ -f "/code/sql/add_foreignkey.sql" ]; then
#     echo "Adding foreign keys..."
#     psql -h db -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /code/sql/add_foreignkey.sql || echo "psql returned non-zero exit code"
# fi

# # 5️⃣ Run Alembic migrations (optional, idempotent)
# ALEMBIC_EXISTS=$(psql -h db -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc "SELECT 1 FROM information_schema.tables WHERE table_name='alembic_version';" 2>/dev/null || true)
# if [ "$ALEMBIC_EXISTS" = "1" ]; then
#     echo "Running Alembic upgrade head..."
#     python -m alembic upgrade head
# else
#     echo "No alembic_version table — stamping head"
#     python -m alembic stamp head
# fi

echo "🚀 Starting application"
exec "$@"
