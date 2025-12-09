# Winter Swimming Location Database

A web service to gather community around winter swimming activity with a global database of swimming locations.

## Features

- Open database of winter swimming locations worldwide
- Easy location submission and community moderation
- Multi-language support (English, Finnish, Estonian)
- Mobile-responsive design
- Interactive map interface

## Tech Stack

- Django 6.0
- PostgreSQL + PostGIS
- Poetry for dependency management
- Vanilla CSS3, HTML, JavaScript
- Leaflet for maps
- django-modeltranslation for multi-language support

## Project Structure

```
winterswim/
├── apps/
│   └── locations/          # Main application
│       ├── models/         # Domain models (entities)
│       ├── services/       # Business logic (functional core)
│       ├── views/          # Web layer (imperative shell)
│       └── forms/          # Django forms
├── config/                 # Django project settings
│   └── settings/           # Split settings (base, development, production)
├── infrastructure/         # Infrastructure layer
│   └── storage/            # Abstract storage backend
├── static/                 # CSS, JavaScript
│   ├── css/
│   │   ├── variables.css   # Theme variables
│   │   └── components/
│   └── js/
├── templates/              # HTML templates
└── media/                  # User uploads
```

## Setup

You can run the application either with Docker (recommended) or manually with Poetry.

### Option 1: Docker Setup (Recommended)

**Prerequisites:**
- Docker
- Docker Compose

**Quick Start:**

1. Clone the repository

2. Copy environment file:
   ```bash
   cp .env.docker.example .env
   # Edit .env with your settings (optional for development)
   ```

3. Start the application:
   ```bash
   docker-compose up -d
   ```

   This will:
   - Start PostgreSQL with PostGIS extension
   - Run database migrations
   - Start the Django development server
   - Make the app available at http://localhost:8000

4. Create a superuser (optional):
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

   Or set these in your `.env` file before starting:
   ```bash
   DJANGO_SUPERUSER_USERNAME=admin
   DJANGO_SUPERUSER_EMAIL=admin@example.com
   DJANGO_SUPERUSER_PASSWORD=changeme123
   ```

**Useful Docker Commands:**

```bash
# View logs
docker-compose logs -f web

# Stop the application
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# Run Django management commands
docker-compose exec web python manage.py <command>

# Access Django shell
docker-compose exec web python manage.py shell

# Access database
docker-compose exec db psql -U postgres -d winterswim
```

**Production Deployment:**

```bash
# Use production configuration
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# This will:
# - Use Gunicorn instead of development server
# - Serve via Nginx reverse proxy (optional)
# - Disable debug mode
# - Enable automatic restarts
```

### Option 2: Manual Setup with Poetry

**Prerequisites:**
- Python 3.12+
- PostgreSQL 14+ with PostGIS extension
- Poetry

**Installation:**

1. Clone the repository

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Set up PostgreSQL database:
   ```bash
   createdb winterswim
   psql winterswim -c "CREATE EXTENSION postgis;"
   ```

4. Copy environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. Run the setup script:
   ```bash
   ./setup.sh
   ```

   Or manually:
   ```bash
   poetry run python manage.py migrate
   poetry run python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   poetry run python manage.py runserver
   ```

## Accessing the Application

Once running, visit:
- **Main site**: http://localhost:8000/
- **Admin panel**: http://localhost:8000/admin/
- **API**: http://localhost:8000/api/locations/

## Development

The project follows the "Functional Core, Imperative Shell" pattern:
- **Models** (`models/`): Pure data structures
- **Services** (`services/`): Business logic (pure functions where possible)
- **Views** (`views/`): Imperative shell that orchestrates services

### Adding Translations

To add or update translations:

1. Make strings translatable in Python code:
   ```python
   from django.utils.translation import gettext_lazy as _
   message = _("Hello world")
   ```

2. Generate translation files:
   ```bash
   poetry run python manage.py makemessages -l fi -l et
   ```

3. Edit translation files in `locale/` directory

4. Compile translations:
   ```bash
   poetry run python manage.py compilemessages
   ```

## License

TBD
