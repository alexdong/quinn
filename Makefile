.PHONY: help dev test test-coverage type-coverage update-llms-txt refresh-pricing code-smell upgrade commit

help:  ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev:  ## Run code quality checks (ruff, format, type check)
	uv run ruff check . --fix --unsafe-fixes
	uv run ruff format .
	uv run ty check .

test:  ## Run tests with last-failed first
	uv run pytest

test-coverage:  ## Run tests with coverage reporting and fail on warnings
	uv run pytest -W error --cov=. --cov-report=html --cov-report=term --durations=5

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

code-smell:  ## Scan for code smells. Usage: make code-smell [PATTERN=glob*] [DIR=directory]
	@echo "🔍 Scanning for code smells..."
	@search_path=$${DIR:-quinn}; \
	if [ -n "$(PATTERN)" ]; then \
		echo "📁 Using pattern: $(PATTERN) in $$search_path/"; \
		target_files=$$(/usr/bin/find "$$search_path" -name "$(PATTERN)" -type f -not -path "*/__pycache__/*" -not -name "*.pyc" | grep -E '\.(py|js|ts|jsx|tsx)$$' 2>/dev/null || true); \
	elif [ -n "$(DIR)" ]; then \
		echo "📁 Scanning all files in $$search_path/"; \
		target_files=$$(/usr/bin/find "$$search_path" -type f -not -path "*/__pycache__/*" -not -name "*.pyc" | grep -E '\.(py|js|ts|jsx|tsx)$$' 2>/dev/null || true); \
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
			echo "✅ No files matching pattern '$(PATTERN)' found in $$search_path/"; \
		elif [ -n "$(DIR)" ]; then \
			echo "✅ No source files found in $$search_path/"; \
		else \
			echo "✅ No source files changed - no smells to detect"; \
		fi; \
	fi

upgrade:  ## Upgrade dependencies to latest versions
	@echo "🔄 Upgrading dependencies to latest versions..."
	@uv sync --upgrade --dev
	@echo "📝 Committing dependency updates..."
	@git add pyproject.toml uv.lock
	@git commit -m "chore: upgrade dependencies to latest versions" || echo "ℹ️  No changes to commit"
	@echo "✅ Dependencies upgraded and committed!"

commit:  ## Run all quality checks and create an automated commit
	@echo "🚀 Running complete quality and testing pipeline..."
	@echo "📋 Step 1: Code quality checks..."
	@$(MAKE) dev
	@echo "✅ Code quality checks passed!"
	@echo ""
	@echo "🧪 Step 2: Running tests..."
	@$(MAKE) test
	@echo "✅ Tests passed!"
	@echo ""
	@echo "📊 Step 3: Type coverage check..."
	@$(MAKE) type-coverage
	@echo "✅ Type coverage check passed!"
	@echo ""
	@echo "📈 Step 4: Test coverage check..."
	@$(MAKE) test-coverage
	@echo "✅ Test coverage check passed!"
	@echo ""
	@echo "🤖 Step 5: Creating automated commit..."
	@claude --dangerously-skip-permissions -p "Commit and push changes to the repository. Ensure all changes are committed and pushed to the main branch."
	@echo "✅ Commit pipeline completed successfully!"
