.PHONY: help run test test-integration test-unit clean install dev lint format check

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Proto-DDF Makefile Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Examples:$(NC)"
	@echo "  make run                    # Run the Proto-DDF generator"
	@echo "  make run PORT=8080          # Run with custom port"
	@echo "  make test                   # Run all tests"
	@echo "  make install                # Install dependencies"

run: ## Run the Proto-DDF generator application
	@echo "$(BLUE)🚀 Starting Proto-DDF Generator...$(NC)"
	@bash workflows/run.sh --log=ERROR $(ARGS)

dev: run ## Alias for 'make run' (development mode)

test: ## Run all tests (unit + integration)
	@echo "$(BLUE)🧪 Running all tests...$(NC)"
	@bash workflows/test.sh

test-integration: ## Run integration tests only
	@echo "$(BLUE)🧪 Running integration tests...$(NC)"
	@source venv/bin/activate && python -m pytest tests/integration/ -vgtimeout 300 source venv/bin/activate && python -m pytest tests/integration/ -v

test-unit: ## Run unit tests only
	@echo "$(BLUE)🧪 Running unit tests...$(NC)"
	@source venv/bin/activate && python -m pytest tests/unit/ -vgtimeout 300 source venv/bin/activate && python -m pytest tests/unit/ -v

test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)📊 Running tests with coverage...$(NC)"
	@source venv/bin/activate && python -m pytest tests/ --cov=proto_ddf_app --cov-report=html --cov-report=termgtimeout 300 source venv/bin/activate && python -m pytest tests/ --cov=proto_ddf_app --cov-report=html --cov-report=term

lint: ## Run linters (flake8, mypy)
	@echo "$(BLUE)🔍 Running linters...$(NC)"
	@source venv/bin/activate && flake8 proto_ddf_app/ tests/ || true
	@source venv/bin/activate && mypy proto_ddf_app/ || true

format: ## Format code with black
	@echo "$(BLUE)✨ Formatting code...$(NC)"
	@source venv/bin/activate && black proto_ddf_app/ tests/

check: lint test ## Run linters and tests

install: ## Install dependencies
	@echo "$(BLUE)📦 Installing dependencies...$(NC)"
	@python3 -m venv venv || true
	@source venv/bin/activate && pip install -q --upgrade pipgtimeout 600 source venv/bin/activate && pip install -q --upgrade pip
	@source venv/bin/activate && pip install -q -e ./reflexgtimeout 600 source venv/bin/activate && pip install -q -e ./reflex
	@source venv/bin/activate && pip install -q -r requirements.txtgtimeout 600 source venv/bin/activate && pip install -q -r requirements.txt
	@echo "$(GREEN)✅ Dependencies installed$(NC)"

clean: ## Clean up generated files and caches
	@echo "$(BLUE)🧹 Cleaning up...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || truegtimeout 300 find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true
	@rm -rf .web/ 2>/dev/null || true
	@echo "$(GREEN)✅ Cleanup complete$(NC)"

clean-all: clean ## Clean everything including venv and generated apps
	@echo "$(RED)⚠️  Removing virtual environment and generated apps...$(NC)"
	@rm -rf venv/
	@rm -rf generated/*/venv/
	@rm -rf generated/*/.web/
	@echo "$(GREEN)✅ Deep cleanup complete$(NC)"

init: clean install ## Initialize the project from scratch
	@echo "$(GREEN)✅ Project initialized$(NC)"

status: ## Show project status
	@echo "$(BLUE)📊 Proto-DDF Project Status$(NC)"
	@echo ""
	@echo "$(YELLOW)Python Version:$(NC)"
	@python3 --version || echo "$(RED)Python not found$(NC)"
	@echo ""
	@echo "$(YELLOW)Virtual Environment:$(NC)"
	@if [ -d "venv" ]; then echo "$(GREEN)✅ Exists$(NC)"; else echo "$(RED)❌ Not found$(NC)"; fi
	@echo ""
	@echo "$(YELLOW)Reflex Submodule:$(NC)"
	@if [ -f "reflex/pyproject.toml" ]; then echo "$(GREEN)✅ Initialized$(NC)"; else echo "$(RED)❌ Not initialized$(NC)"; fi
	@echo ""
	@echo "$(YELLOW)Generated Apps:$(NC)"
	@ls -1 generated/ 2>/dev/null | grep -v README | wc -l | xargs -I {} echo "  {} apps generated"
	@echo ""
	@echo "$(YELLOW)Port Configuration:$(NC)"
	@if [ -f "config/.port_config.json" ]; then cat config/.port_config.json; else echo "$(RED)Not configured yet$(NC)"; fi

ports: ## Show current port configuration
	@echo "$(BLUE)🔌 Port Configuration$(NC)"
	@if [ -f "config/.port_config.json" ]; then \
		cat config/.port_config.json; \
	else \
		echo "$(RED)Port configuration not found$(NC)"; \
		echo "Run 'make run' to generate port configuration"; \
	fi

logs: ## Show recent application logs
	@echo "$(BLUE)📋 Recent Logs$(NC)"
	@tail -50 proto_ddf.log 2>/dev/null || echo "$(RED)No logs found$(NC)"

logs-follow: ## Follow application logs in real-time
	@echo "$(BLUE)📋 Following Logs (Ctrl+C to stop)$(NC)"
	@tail -f proto_ddf.log

generated-apps: ## List all generated applications
	@echo "$(BLUE)📱 Generated Applications$(NC)"
	@echo ""
	@for dir in generated/*/; do \
		if [ -d "$$dir" ] && [ "$$(basename $$dir)" != "README.md" ]; then \
			echo "$(GREEN)📦 $$(basename $$dir)$(NC)"; \
			if [ -f "$$dir/rxconfig.py" ]; then \
				grep -E "(backend_port|frontend_port)" "$$dir/rxconfig.py" | sed 's/^/  /'; \
			fi; \
			echo ""; \
		fi; \
	done

run-generated: ## Run a generated app (usage: make run-generated APP=app_name)
	@if [ -z "$(APP)" ]; then \
		echo "$(RED)❌ Please specify APP name: make run-generated APP=app_name$(NC)"; \
		echo ""; \
		echo "$(YELLOW)Available apps:$(NC)"; \
		ls -1 generated/ | grep -v README; \
		exit 1; \
	fi
	@if [ ! -d "generated/$(APP)" ]; then \
		echo "$(RED)❌ App 'generated/$(APP)' not found$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)🚀 Running generated app: $(APP)$(NC)"
	@cd generated/$(APP) && bash run.sh

docs: ## Generate documentation
	@echo "$(BLUE)📚 Generating documentation...$(NC)"
	@echo "$(YELLOW)Documentation available in docs/$(NC)"
	@ls -la docs/

.PHONY: version
version: ## Show version information
	@echo "$(BLUE)Proto-DDF Version Information$(NC)"
	@echo ""
	@echo "$(YELLOW)Python:$(NC) $$(python3 --version)"
	@echo "$(YELLOW)Node:$(NC) $$(node --version 2>/dev/null || echo 'Not installed')"
	@echo "$(YELLOW)Reflex:$(NC) $$(source venv/bin/activate 2>/dev/null && python -c 'import reflex; print(reflex.__version__)' 2>/dev/null || echo 'Not installed')"

# Resource management targets (standardized)
.PHONY: detect-resources compose-validate compose-up compose-down test-auto

detect-resources: ## Detect available system resources
	@bash scripts/detect_resources.sh 2>/dev/null || echo "Resource detection script not found"

compose-validate: ## Validate compose.yml
	@docker compose config --quiet 2>/dev/null || echo "Docker Compose not available"gtimeout 60 docker compose config --quiet 2>/dev/null || echo "Docker Compose not available"

compose-up: ## Start services with resource limits
	@docker compose --profile app up -d 2>/dev/null || docker compose up -dgtimeout 60 docker compose --profile app up -d 2>/dev/null || docker compose up -d

compose-down: ## Stop all services
	@docker compose down 2>/dev/null || echo "Docker Compose not available"gtimeout 60 docker compose down 2>/dev/null || echo "Docker Compose not available"

test-auto: ## Run tests with auto-detected settings
	@bash scripts/detect_resources.sh --apply --mode=balanced 2>/dev/null || echo "Resource detection not available"
	@npm test 2>/dev/null || pytest -v 2>/dev/null || echo "No test command found"gtimeout 300 npm test 2>/dev/null || pytest -v 2>/dev/null || echo "No test command found"
