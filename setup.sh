#!/bin/bash

# Setup script for Winter Swimming Location Database
# This script helps initialize the development environment

set -e

echo "🏊 Winter Swimming Location Database - Setup Script"
echo "=================================================="
echo ""

# Check if PostgreSQL is running
if ! pg_isready -q; then
    echo "❌ PostgreSQL is not running. Please start PostgreSQL first."
    exit 1
fi

echo "✓ PostgreSQL is running"

# Check if database exists
DB_NAME=${DB_NAME:-winterswim}
if psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo "✓ Database '$DB_NAME' already exists"
else
    echo "Creating database '$DB_NAME'..."
    createdb "$DB_NAME"
    echo "✓ Database created"
fi

# Enable PostGIS extension
echo "Enabling PostGIS extension..."
psql "$DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS postgis;"
echo "✓ PostGIS enabled"

# Run migrations
echo ""
echo "Running Django migrations..."
poetry run python manage.py makemigrations
poetry run python manage.py migrate
echo "✓ Migrations complete"

# Create locale directory for translations
echo ""
echo "Setting up translations..."
mkdir -p locale
poetry run python manage.py makemessages -l fi -l et --ignore=env --ignore=venv
echo "✓ Translation files created"

# Compile translations
poetry run python manage.py compilemessages
echo "✓ Translations compiled"

# Collect static files
echo ""
echo "Collecting static files..."
poetry run python manage.py collectstatic --noinput
echo "✓ Static files collected"

# Create superuser
echo ""
echo "Would you like to create a superuser account? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    poetry run python manage.py createsuperuser
fi

echo ""
echo "=================================================="
echo "✓ Setup complete!"
echo ""
echo "To start the development server:"
echo "  poetry run python manage.py runserver"
echo ""
echo "Then visit:"
echo "  http://localhost:8000/ - Main site"
echo "  http://localhost:8000/admin/ - Admin interface"
echo ""
