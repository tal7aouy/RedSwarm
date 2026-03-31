.PHONY: help setup install dev build test clean

help:
	@echo "RedSwarm - Available Commands"
	@echo "=============================="
	@echo "setup          - Initial setup (create .env, install deps)"
	@echo "install        - Install all dependencies"
	@echo "dev            - Run backend + frontend (see README)"
	@echo "build          - Build production bundles"
	@echo "test           - Run all tests"
	@echo "clean          - Clean build artifacts"

setup:
	@echo "🔴 Setting up RedSwarm..."
	@chmod +x setup.sh
	@./setup.sh

install:
	@echo "Installing backend dependencies..."
	@cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	@cd frontend && npm install

dev:
	@echo "Starting development servers..."
	@npm run dev

build:
	@echo "Building production bundles..."
	@cd frontend && npm run build

test:
	@echo "Running backend tests..."
	@cd backend && pytest
	@echo "Running frontend tests..."
	@cd frontend && npm run test

clean:
	@echo "Cleaning build artifacts..."
	@rm -rf backend/__pycache__
	@rm -rf backend/**/__pycache__
	@rm -rf backend/.pytest_cache
	@rm -rf frontend/dist
	@rm -rf frontend/node_modules/.vite
	@echo "Clean complete!"
