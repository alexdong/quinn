.PHONY: dev test test-coverage type-coverage update-llms-txt refresh-pricing

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

refresh-pricing:
	@echo "📊 Refreshing LLM pricing data..."
	@mkdir -p quinn/agent/pricing
	@claude --dangerously-skip-permissions -p "Fetch the latest pricing for these models from their official provider websites and create/update JSON files in quinn/agent/pricing/\nInclude both regular and cached input pricing.\n:\n\n1. OpenAI (https://platform.openai.com/docs/pricing): Create openai.json with:\n   - gpt-4o-mini\n   - o3\n   - o4-mini\n   - gpt-4.1\n   - gpt-4.1-mini\n   - gpt-4.1-nano\n   \n2. Anthropic (https://www.anthropic.com/pricing): Create anthropic.json with:\n   - claude-3-5-sonnet-20241022\n   - claude-opus-4-20250514\n   - claude-sonnet-4\n   - claude-haiku-3.5\n\n3. Google (https://ai.google.dev/gemini-api/docs/pricing): Create google.json with:\n   - gemini-2.0-flash\n   - gemini-2.5-flash-exp\n   - gemini-2.5-pro\n   - gemini-2.5-flash\n\nEach JSON should include:\n- last_updated: current date\n- source_url: provider pricing page\n- models: object with model names as keys, each containing:\n  - input_price_per_1m_tokens\n  - output_price_per_1m_tokens\n  - cached_input_price_per_1m_tokens\n All prices in USD\n\nUse exact model names as they appear in our config.py file or as documented by the provider."
	@echo "✅ Pricing data updated!"
