# Docker Setup Guide

This guide covers running the Winter Swimming Location Database with Docker.

## Quick Start (3 steps)

```bash
# 1. Copy environment file
cp .env.docker.example .env

# 2. Start everything
docker-compose up -d

# 3. Visit http://localhost:8000
```

That's it! The application is now running with PostgreSQL + PostGIS.

## Using the Makefile

For convenience, you can use the Makefile for common commands:

```bash
make up              # Start services
make logs            # View logs
make down            # Stop services
make shell           # Django shell
make dbshell         # Database shell
make createsuperuser # Create admin user
```

Run `make help` to see all available commands.

## Architecture

The Docker setup consists of:

- **db**: PostgreSQL 16 with PostGIS 3.4 extension
- **web**: Django application running on port 8000
- **nginx** (production only): Reverse proxy for static files and SSL

### Volumes

Three persistent volumes are created:
- `postgres_data`: Database files
- `media_data`: User-uploaded images
- `static_data`: Collected static files

## Development Workflow

### Hot Reload

The development setup mounts your local code into the container, so changes are reflected immediately without rebuilding:

```bash
# Edit any Python file
# Changes are live - no need to rebuild!
```

### Running Migrations

After modifying models:

```bash
make makemigrations
make migrate
```

Or directly:

```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

### Adding Dependencies

When you add a new package to `pyproject.toml`:

```bash
# Rebuild the image
docker-compose up -d --build
```

### Accessing Logs

```bash
# All services
docker-compose logs -f

# Just the web app
docker-compose logs -f web

# Just the database
docker-compose logs -f db
```

### Database Access

Access the PostgreSQL database:

```bash
docker-compose exec db psql -U postgres -d winterswim
```

Or use the Makefile:

```bash
make dbshell
```

## Environment Variables

The `.env` file controls configuration:

```bash
# Django settings
DJANGO_ENV=development           # 'development' or 'production'
DJANGO_SECRET_KEY=secret123     # Change in production!
DEBUG=True                       # Set to False in production
ALLOWED_HOSTS=localhost         # Comma-separated list

# Database
DB_NAME=winterswim
DB_USER=postgres
DB_PASSWORD=postgres

# Auto-create superuser (optional)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=changeme123
```

## Production Deployment

### Using docker-compose.prod.yml

```bash
# 1. Update .env for production
cat > .env <<EOF
DJANGO_ENV=production
DJANGO_SECRET_KEY=$(openssl rand -base64 32)
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_PASSWORD=$(openssl rand -base64 16)
EOF

# 2. Start with production config
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Or use the Makefile
make prod-up
```

### Production Features

The production setup includes:
- **Gunicorn** WSGI server (4 workers)
- **Nginx** reverse proxy (optional)
- Automatic service restart on failure
- Static file serving via Nginx
- Health checks

### SSL Certificates

To enable HTTPS:

1. Place certificates in `./certs/`:
   ```
   certs/
   ├── fullchain.pem
   └── privkey.pem
   ```

2. Uncomment the HTTPS server block in `nginx.conf`

3. Restart: `make prod-down && make prod-up`

## Troubleshooting

### Database connection errors

If you see "could not connect to server":

```bash
# Check if database is ready
docker-compose exec db pg_isready

# Restart services
docker-compose restart
```

### Port already in use

If port 8000 is already in use:

```bash
# Change port in .env
WEB_PORT=8001

# Restart
docker-compose up -d
```

### Permission denied

If you see permission errors with volumes:

```bash
# Fix ownership
docker-compose exec web chown -R appuser:appuser /app/media /app/staticfiles
```

### Reset everything

To start fresh:

```bash
# WARNING: This deletes all data!
make clean

# Or manually
docker-compose down -v
rm -rf media/ staticfiles/
```

## Docker Commands Reference

### Container Management

```bash
docker-compose up              # Start (foreground)
docker-compose up -d           # Start (background)
docker-compose down            # Stop and remove containers
docker-compose restart         # Restart services
docker-compose ps              # List running services
```

### Logs

```bash
docker-compose logs            # View all logs
docker-compose logs -f         # Follow logs (live)
docker-compose logs -f web     # Follow specific service
docker-compose logs --tail=100 # Last 100 lines
```

### Execute Commands

```bash
docker-compose exec web <command>        # Run in web container
docker-compose exec web python manage.py shell
docker-compose exec web python manage.py test
docker-compose exec db psql -U postgres
```

### Building

```bash
docker-compose build           # Build all images
docker-compose build --no-cache  # Build without cache
docker-compose up -d --build   # Rebuild and start
```

### Cleanup

```bash
docker-compose down            # Stop and remove containers
docker-compose down -v         # Also remove volumes
docker system prune -a         # Clean up unused images
```

## Performance Tips

### Database Performance

For better performance in production, add to `docker-compose.yml`:

```yaml
db:
  command: postgres -c shared_buffers=256MB -c max_connections=200
```

### Web Workers

Adjust Gunicorn workers based on your server:

```yaml
web:
  command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 8
```

Rule of thumb: `workers = (2 × CPU cores) + 1`

## Backup and Restore

### Backup Database

```bash
docker-compose exec db pg_dump -U postgres winterswim > backup.sql
```

### Restore Database

```bash
cat backup.sql | docker-compose exec -T db psql -U postgres winterswim
```

### Backup Media Files

```bash
docker cp winterswim-web:/app/media ./media_backup
```

## Next Steps

- Set up CI/CD pipeline
- Add monitoring (Sentry, Prometheus)
- Configure CDN for static files
- Set up database backups
- Add Redis for caching
- Configure email service

## Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/)
- [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)
- [PostGIS Docker Hub](https://hub.docker.com/r/postgis/postgis)
