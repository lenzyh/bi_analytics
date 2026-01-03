# BI Analytics Demo Makefile
# Convenient commands for development and demo management

.PHONY: help install run clean test format lint demo

help: ## Show this help message
	@echo "BI Analytics Platform Demo"
	@echo "========================="
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies using uv
	@echo "📦 Installing dependencies with uv..."
	uv sync

install-pip: ## Install dependencies using pip (fallback)
	@echo "📦 Installing dependencies with pip..."
	python -m venv venv
	source venv/bin/activate && pip install -r requirements.txt

run: ## Run the Streamlit demo
	@echo "🚀 Starting BI Analytics Demo..."
	uv run streamlit run app.py

demo: ## Run the demo using the launcher script
	@echo "🎪 Starting demo presentation..."
	uv run python run_demo.py

clean: ## Clean up generated files and cache
	@echo "🧹 Cleaning up..."
	rm -rf .venv/
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf *.egg-info/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

format: ## Format code with black
	@echo "🎨 Formatting code..."
	uv run black app.py run_demo.py

lint: ## Lint code with flake8
	@echo "🔍 Linting code..."
	uv run flake8 app.py run_demo.py

test: ## Run tests (placeholder)
	@echo "🧪 Running tests..."
	@echo "No tests configured yet"

dev-install: ## Install development dependencies
	@echo "🛠️ Installing development dependencies..."
	uv sync --extra dev

check: format lint ## Run all code quality checks
	@echo "✅ All checks completed"

setup: install ## Initial setup for new users
	@echo "🎯 Setup completed! Run 'make demo' to start the presentation"

# Docker commands (if needed)
docker-build: ## Build Docker image
	@echo "🐳 Building Docker image..."
	docker build -t bi-analytics-demo .

docker-run: ## Run Docker container
	@echo "🐳 Running Docker container..."
	docker run -p 8501:8501 bi-analytics-demo

# Environment info
info: ## Show environment information
	@echo "Environment Information:"
	@echo "======================="
	@echo "Python version: $(shell python --version)"
	@echo "uv version: $(shell uv --version 2>/dev/null || echo 'uv not installed')"
	@echo "Current directory: $(shell pwd)"
	@echo "Virtual environment: $(shell echo $$VIRTUAL_ENV)"

# Quick demo for presentations
present: ## Quick presentation setup
	@echo "🎪 Setting up for client presentation..."
	@echo "1. Installing dependencies..."
	@make install > /dev/null 2>&1
	@echo "2. Starting demo..."
	@make demo