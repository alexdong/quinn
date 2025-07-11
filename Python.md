# Python Coding Standards for AI Agents

## Core Philosophy

**We are a one-person army. Readability after a long hiatus is crucial.**

This core requirement sets the tone for all coding practices. Code must be understandable after not touching it for months or years. This requires simple, shorter code with clear data flow and state transitions that are easy to trace.

### Planning and Documentation

Documentation that lives close to code is more likely to stay current. TODO lists provide clear progress tracking.

- Add "Implementation Plan (TODOs)" section to `logs/{FeatureName}.md`
- Use nested itemized lists with `[ ]` prefixes for TODO items
- Tick off completed items and add implementation notes
- Log improvements in `logs/{FeatureName}-Improvements.log`

### Code Quality Checks (Sequential)

Automated checks catch issues early and maintain consistency. Running them in sequence prevents later tools from being confused by earlier failures.

- `uv run ruff format {files}`
- `uv run ruff check {files}`
- `uv run ty {files}`
- `uv run pytest -vv {files}_test.py` (minimum tests for changes)

### Iterative Development Process

After you generate code, don't stop at the first pass. Instead, iteratively improve the generated code until you can't make it any better. Make it more readable, succinct. Focus on one particular enhancement each iteration. You must keep going until you can not find further ways to improve the code.


## Development Environment

### Core Tools
- **Python**: 3.12+
- **Package Management**: `uv` (not pip or requirements.txt)
- **Code Quality**: 
  - `ruff` (formatting and linting), 
  - `ty` (type checking), 
  - `pydantic` (more sophisticated types and data validation)
- **Testing**: `pytest`
- **CLI Tools**: `click`, `prompt-toolkit`, `rich`
- **Web**: `fasthtml`
- **Templates**: `jinja2`
- **AI/LLM**: 
  - `pydantic-ai` (Agent and structured output and validation), 
  - OpenAI Whisper (audio)
- **Data & Analysis**: `numpy`, `plotly`, `streamlit`
- **Hosting**: `ngrok`

### System Environment
- **OS**: macOS 15.5+ or latest Ubuntu (both with complete dev toolchain installed)
- **Shell**: Latest zsh and oh-my-zsh
- **API Access**: Claude and OpenAI API keys via environment variables

### Rust CLI Tools
These tools provide superior performance and ergonomics for common development tasks:
- `curl` - HTTP client with better output formatting than system curl
- `jq` - JSON processor for parsing and manipulating JSON data
- `hyperfine` - Command-line benchmarking tool for performance testing
- `rg` - Fast text search tool (alternative to grep)
- `fd` - Fast file finder (alternative to find)
- `broot` - Interactive directory tree navigation
- `htmlq` - HTML parser and selector tool for web scraping
- `mise` - Development environment and version manager
- `llm` - Command-line interface for various language models
- `monolith` - Tool for saving complete web pages as single HTML files
- `rnr` - Bulk file renaming utility with regex support
- `tspin` - Log file viewer with syntax highlighting and filtering
- `imagemagick/convert` - Image manipulation and conversion
- `ffmpeg` - Video and audio processing
- `sox` - Audio file manipulation
- `audacity` - Audio editing (when GUI is available)
- `yt-dlp` - YouTube and video platform downloader

## Project Structure

```
./
├── docs/                   # Documentation and plans
├── src/                    # Application code
│   ├── component/          # Component specific code and unit tests.
│   ├── utils/              # Component specific code and unit tests.
├── tests/
│   ├── integration/        # Integration tests
│   └── e2e/                # End-to-end tests
├── logs/                   # Implementation logs and progress tracking
├── .stubs/                 # Type stub files for 3rd party libraries
└── Makefile                # Task automation
└── pyproject.toml          # Project setting
```

## Coding Conventions

### Readability First

Code is read far more often than it's written. After months away from code, we need to understand it quickly without archaeological investigation.

- Put the top-level function at the top of each file (read top to bottom)
- Produce compact code - fewer lines mean less cognitive load
- Choose names wisely to minimize effort required to understand intent
- Use long, descriptive names for files, functions, and variables
- Use non-`async` Python calls whenever possible
- Use one-liners (lambda, list comprehensions) to reduce line count
- Prefer simple code over clever hacks
- Use latest Python facilities: dictionary operators (`|`, `|=`), walrus operator (`:=`), structural pattern matching

### Fail Early and Fast

Debugging issues discovered late in execution is exponentially more expensive than catching them early. Clear failure points reduce investigation time.

- Prefer `assert` over `Optional` and try/except for clearer intent
- Use `try` and `except` sparingly - let code fail early
- Use generous `assert` statements to check validity and fail fast
- Use `assert` at the beginning and end of each function to enforce design contracts
- Use descriptive assert messages to document program flow and states

### Minimize Mental Constructs

Every additional abstraction layer increases cognitive load. Functions are easier to understand and test than classes for most use cases.

- Prefer functions over classes
- Write docstrings only when function intention is unclear from name/implementation

### Traceability and Debugging

When code fails (and it will), we need to quickly understand what happened and where. Logs are our time machine for understanding past execution.

- Use logging extensively to document key actions and state transitions
- Set log levels carefully 
- When debugging, use `--debug-modules module1,module2` for selective debug logging
- Include "trace_id" and "span_id" in log messages for multi-component requests
- Use `@functools.wraps` decorators to separate tracing from functional code

### Code Organization

Visual structure helps rapid comprehension. Consistent formatting reduces the mental effort needed to parse code structure.

- Use one empty line between key concept blocks within functions
- Use two empty lines between functions and classes
- Use plain SQL over ORMs and output SQL in logs
- Prefer simple data constructs like `@dataclass`, named tuples, dicts, lists
- Prefer functions over classes
- Refactor high McCabe complexity code and extract common code to `src/utils/`


### Comprehensive Type Coverage

Types serve as executable documentation and catch errors at development time rather than runtime. They make refactoring safer and IDE assistance more powerful.

- Ensure 100% type coverage for easier function purpose tracking through `make type-coverage`
- Prefer tight type annotations. Use specific types over generic ones where possible

### Database Strategy

SQLite provides ACID guarantees without infrastructure complexity. Raw SQL is easier to debug than ORM-generated queries.

- Use SQLite for data persistence
- Use separate SQLite files for different purposes
- Use in-memory SQLite (`sqlite:///:memory:`) for testing
- Use `conftest.py` for test database setup
- Avoid ORMs - use raw SQL for debugging clarity


### When to Comment
*Good code should read like well-written prose. Comments should explain why, not what.*

- Produce comments only when absolutely necessary
- Let code be self-documenting through clear naming
- Use assert messages as inline documentation
- Document complex algorithms or business logic that isn't obvious


### __main__ Block Requirements

Every Python file should be executable for testing and demonstration. This enables quick verification of functionality.

- Include `if __name__ == "__main__"` block in every script
- Make `__main__` function available for every script
- Use `__main__` function to demonstrate usage and test code
- Enable direct CLI invocation of functions within files


## Testing Strategy

### Test Organization

Tests are the safety net for refactoring and the specification for expected behavior. They should be as readable as the production code.

- Name test files `{feature}_test.py` in the same folder as `{feature}.py`
- Prefer functions recognizable by `pytest` over test classes
- Use plain `assert` statements for clarity
- Use `print` in tests for additional runtime details
- Use `pytest.approx` with two decimal points for float/decimal comparisons
- Use `@pytest.mark.parametrize` to separate code from test data
- Use `@pytest.mark.{category}` and `@pytest.mark.requirement({FeatureName})` for test categorization

### Test-Driven Development

Writing tests first clarifies requirements and ensures testable design. It prevents the common trap of writing code that's hard to test.

- Generate test code before application code
- Use detailed assert statements to capture intent and contracts
- Whenever you make a simple change, run the minimum test sets leveraging `pytest. mark`.


### Regression Testing

Full regression testing ensures changes don't break existing functionality. Coverage metrics indicate test quality.

- Single-module: `PYTHONPATH=$(pwd) uv run pytest -vv --cov=module_name --durations=4`
- Multi-module: `PYTHONPATH=$(pwd) uv run pytest -vv --cov=src --durations=4`
- Coverage requirement: Minimum 84%
- Performance: Optimize tests that take too long to execute


## Build and Deployment

### Makefile Usage

Makefiles provide discoverable, consistent commands across projects. They reduce cognitive load by standardizing common tasks.

- Create Makefile entries for linting, testing, deployment
- Keep comments succinct and relevant
- Refactor repeated commands into Makefile targets

### Git Workflow

Frequent commits with clear messages provide better project history and easier debugging.

- Commit and push after completing each TODO item
- Include meaningful commit messages describing changes