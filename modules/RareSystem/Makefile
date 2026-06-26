# Makefile for Rare Disease Genetic Diagnosis System
# Usage: make <command>

.PHONY: help build run stop dev clean logs shell test

# Default target
help:
	@echo "Rare Disease Genetic Diagnosis System - Docker Commands"
	@echo ""
	@echo "Usage: make <command>"
	@echo ""
	@echo "Commands:"
	@echo "  build    Build Docker images"
	@echo "  run      Run the application (production mode)"
	@echo "  stop     Stop the application"
	@echo "  dev      Run in development mode with hot reload"
	@echo "  clean    Remove containers, images, and volumes"
	@echo "  logs     View application logs"
	@echo "  shell    Open a shell in the container"
	@echo "  test     Run tests"
	@echo ""

# Build Docker images
build:
	@echo "Building Docker images..."
	docker-compose build

# Run the application
run:
	@echo "Starting application..."
	docker-compose up -d
	@echo ""
	@echo "Application is running:"
	@echo "  Frontend: http://localhost"
	@echo "  Backend API: http://localhost:8000"
	@echo "  API Docs: http://localhost:8000/docs"

# Stop the application
stop:
	@echo "Stopping application..."
	docker-compose down

# Development mode
dev:
	@echo "Starting development environment..."
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Clean up
clean:
	@echo "Cleaning up..."
	docker-compose down -v --rmi local
	docker system prune -f

# View logs
logs:
	docker-compose logs -f

# Open shell
shell:
	docker exec -it rare-disease-app /bin/bash

# Run tests
test:
	@echo "Running tests..."
	docker exec -it rare-disease-app python -m pytest /app/tests

# Quick start (build and run)
quickstart: build run
	@echo "Quick start complete!"

# Production build with no cache
build-prod:
	@echo "Building production images (no cache)..."
	docker-compose build --no-cache

# Check status
status:
	@docker-compose ps

# Restart application
restart: stop run
