.PHONY: dev test test-coverage type-coverage update-llms-txt

dev:
	uv run ruff check . --fix --unsafe-fixes
	uv run ruff format .
	uv run ty check .

test:
	pytest --lf

test-coverage:
	pytest --cov=. --cov-report=html --cov-report=term --duration=5 

type-coverage:
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

update-llms-txt:
	@echo "📚 Updating llms/*.txt documentation files..."
	@mkdir -p llms
	@claude -p "Please update the llms/ directory with documentation for tools mentioned in Python.md. For each tool: \
	\
	1. CLI TOOLS: Run '{tool} --help' to get help output. Save to llms/{tool}.txt. \
	2. PYTHON PACKAGES: Check for official llms.txt files at common locations: \
	   - https://docs.{package}.dev/latest/llms.txt or llms-full.txt \
	   - https://{package}.readthedocs.io/llms.txt \
	   - For pydantic-ai: https://ai.pydantic.dev/llms-full.txt \
	   - For fasthtml: https://fastht.ml/docs/llms-ctx-full.txt \
	3. For each file, add a footer documenting: \
	   - Source URL or command used \
	   - Retrieval date \
	   - Method (curl, help command, etc.) \
	\
	IMPORTANT: Only update existing files or create new ones for tools in Python.md. Use curl to download llms.txt files when available. For CLI tools not installed, create placeholder noting unavailability."
	@echo "✅ llms/*.txt files updated!"
