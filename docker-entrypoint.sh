#!/bin/bash

# Docker entrypoint script for Winter Swimming app
# Handles database initialization and migrations

set -e

echo "🏊 Winter Swimming - Docker Entrypoint"
echo "======================================"

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
while ! pg_isready -h "${DB_HOST:-db}" -p "${DB_PORT:-5432}" -U "${DB_USER:-postgres}" > /dev/null 2>&1; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 1
done
echo "✓ PostgreSQL is ready"

# Run migrations
echo ""
echo "Running database migrations..."
python manage.py migrate --noinput
echo "✓ Migrations complete"

# Create translations if they don't exist
echo ""
echo "Setting up translations..."
if [ ! -d "locale/fi" ] || [ ! -d "locale/et" ]; then
    echo "Creating translation files..."
    python manage.py makemessages -l fi -l et --ignore=env --ignore=venv --ignore=.venv || true
fi

# Compile translations
echo "Compiling translations..."
python manage.py compilemessages || true
echo "✓ Translations ready"

# Collect static files
echo ""
echo "Collecting static files..."
python manage.py collectstatic --noinput
echo "✓ Static files collected"

# Create superuser if environment variables are set
if [ -n "${DJANGO_SUPERUSER_USERNAME}" ] && [ -n "${DJANGO_SUPERUSER_EMAIL}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD}" ]; then
    echo ""
    echo "Creating superuser..."
    python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='${DJANGO_SUPERUSER_USERNAME}').exists():
    User.objects.create_superuser('${DJANGO_SUPERUSER_USERNAME}', '${DJANGO_SUPERUSER_EMAIL}', '${DJANGO_SUPERUSER_PASSWORD}')
    print('✓ Superuser created')
else:
    print('✓ Superuser already exists')
EOF
fi

echo ""
echo "======================================"
echo "✓ Initialization complete!"
echo ""

# Execute the command passed to docker run
exec "$@"
