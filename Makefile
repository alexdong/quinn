.PHONY: help dev test test-coverage type-coverage update-llms-txt refresh-pricing codesmell

help:  ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev:  ## Run code quality checks (ruff, format, type check)
	uv run ruff check . --fix --unsafe-fixes
	uv run ruff format .
	uv run ty check .

test:  ## Run tests with last-failed first
	pytest --lf

test-coverage:  ## Run tests with coverage reporting
	pytest --cov=. --cov-report=html --cov-report=term --duration=5 

type-coverage:  ## Check type annotation coverage and quality
	@echo "🔍 Checking type annotation coverage..."
	@echo "📊 Checking for missing return type annotations..."
	@uv run ruff check . --select ANN201 --quiet || echo "❌ Missing return type annotations found"
	@echo "📊 Checking for missing parameter type annotations..."
	@uv run ruff check . --select ANN001,ANN002,ANN003 --quiet || echo "❌ Missing parameter type annotations found"
	@echo "📊 Running comprehensive type check..."
	@uv run ty check . > /dev/null 2>&1 && echo "✅ Type checking passed - excellent coverage!" || echo "❌ Type checking failed"
	@echo "📊 Checking for Any usage (should be minimal)..."
	@uv run ruff check . --select ANN401 --quiet && echo "✅ No problematic Any usage found" || echo "⚠️  Some Any usage found (may be acceptable in tests)"
	@echo "📈 Type coverage assessment complete!"

update-llms-txt:  ## Update llm documentation files. Usage: make update-llms-txt [PATTERN=tool_name]
	@echo "📚 Updating llms/*.txt documentation files..."
	@mkdir -p llms
	@if [ -n "$(PATTERN)" ]; then \
		echo "📁 Updating only files matching pattern: $(PATTERN)"; \
		claude -p "$$(cat tools/refresh_llms_txt.md) Focus only on tools matching pattern '$(PATTERN)'."; \
	else \
		echo "📁 Updating all tools from Python.md"; \
		claude -p "$$(cat tools/refresh_llms_txt.md)"; \
	fi
	@echo "✅ llms/*.txt files updated!"

refresh-pricing:  ## Refresh LLM pricing data from provider websites
	@echo "📊 Refreshing LLM pricing data..."
	@mkdir -p quinn/agent/pricing
	@claude --dangerously-skip-permissions -p "$$(cat tools/refresh_llm_pricing.md)"
	@echo "✅ Pricing data updated!"

codesmell:  ## Scan for code smells in changed files or pattern. Usage: make codesmell [PATTERN=glob*]
	@echo "🔍 Scanning for code smells..."
	@if [ -n "$(PATTERN)" ]; then \
		echo "📁 Using pattern: $(PATTERN)"; \
		target_files=$$(find quinn -name "$(PATTERN)" -type f | grep -E '\.(py|js|ts|jsx|tsx)$$' 2>/dev/null || true); \
	else \
		echo "📁 Using git diff (changed files):"; \
		target_files=$$(git diff --name-only --diff-filter=AMR | grep -E '\.(py|js|ts|jsx|tsx)$$'); \
	fi; \
	if [ -n "$$target_files" ]; then \
		echo "$$target_files" | sed 's/^/   - /'; \
		echo ""; \
		echo "🧹 Running code smell detection..."; \
		claude -p "$$(cat tools/code_smell.md)" "$$target_files"; \
	else \
		if [ -n "$(PATTERN)" ]; then \
			echo "✅ No files matching pattern '$(PATTERN)' found"; \
		else \
			echo "✅ No source files changed - no smells to detect"; \
		fi; \
	fi
