.PHONY: help build up down restart logs shell dbshell migrate makemigrations createsuperuser test clean

# Default target
help:
	@echo "Winter Swimming Location Database - Docker Commands"
	@echo "===================================================="
	@echo ""
	@echo "Development commands:"
	@echo "  make build          - Build Docker images"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make logs           - View logs (press Ctrl+C to exit)"
	@echo "  make shell          - Access Django shell"
	@echo "  make dbshell        - Access PostgreSQL shell"
	@echo ""
	@echo "Database commands:"
	@echo "  make migrate        - Run database migrations"
	@echo "  make makemigrations - Create new migrations"
	@echo "  make createsuperuser - Create Django superuser"
	@echo ""
	@echo "Utility commands:"
	@echo "  make test           - Run tests"
	@echo "  make clean          - Remove all containers and volumes"
	@echo ""
	@echo "Production commands:"
	@echo "  make prod-up        - Start in production mode"
	@echo "  make prod-down      - Stop production services"

# Development commands
build:
	docker-compose build

up:
	docker-compose up -d
	@echo ""
	@echo "✓ Services started!"
	@echo "Visit http://localhost:8000"
	@echo ""
	@echo "View logs: make logs"

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

shell:
	docker-compose exec web python manage.py shell

dbshell:
	docker-compose exec db psql -U postgres -d winterswim

# Database commands
migrate:
	docker-compose exec web python manage.py migrate

makemigrations:
	docker-compose exec web python manage.py makemigrations

createsuperuser:
	docker-compose exec web python manage.py createsuperuser

# Utility commands
test:
	docker-compose exec web python manage.py test

clean:
	docker-compose down -v
	@echo "✓ All containers and volumes removed"

# Production commands
prod-up:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo ""
	@echo "✓ Production services started!"

prod-down:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

# Translation commands
makemessages:
	docker-compose exec web python manage.py makemessages -l fi -l et

compilemessages:
	docker-compose exec web python manage.py compilemessages

# Collect static files
collectstatic:
	docker-compose exec web python manage.py collectstatic --noinput
