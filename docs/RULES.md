# Code Smells & Antipatterns

Code smells are patterns that indicate potential issues in code quality, maintainability, or performance. They are not necessarily bugs but can lead to problems if not addressed. This guide shows common antipatterns and their improved alternatives, with real examples from the Quinn codebase.

**Key Principles:**
- **Fail Fast**: Use assertions to catch problems early rather than defensive programming
- **Be Explicit**: Clear, self-documenting code is better than clever code
- **Minimize Cognitive Load**: Reduce nesting, use meaningful names, structure data clearly
- **Performance Matters**: Load heavy resources once, avoid repeated work

## 1. Replace Defensive try/except with Assertions
**Problem:** Defensive exception handling masks real issues and makes debugging harder
**Solution:** Use assertions for precondition validation, let real errors bubble up

**Why this matters:**
- Assertions fail fast with clear error messages
- Eliminates silent failures and None returns
- Makes function contracts explicit
- Reduces cognitive load by removing nested error handling

```python
# Bad: Defensive exception handling masks issues
def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    try:
        if model and model in MODEL_PRICING:
            if input_tokens >= 0 and output_tokens >= 0:
                pricing = MODEL_PRICING[model]
                if "input_price_per_1m_tokens" in pricing:
                    return (input_tokens * pricing["input_price_per_1m_tokens"] + 
                            output_tokens * pricing["output_price_per_1m_tokens"]) / 1_000_000
        return 0.0  # Silent failure!
    except Exception as e:
        logger.error(f"Cost calculation error: {e}")
        return 0.0  # Masks the real problem

# Good: Clear assertions with descriptive messages
def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate cost for LLM usage with clear precondition validation."""
    assert model.strip(), "Model name cannot be empty"
    assert model in MODEL_PRICING, f"Model {model} not found in pricing data"
    assert input_tokens >= 0, f"Input tokens must be non-negative, got {input_tokens}"
    assert output_tokens >= 0, f"Output tokens must be non-negative, got {output_tokens}"
    
    pricing = MODEL_PRICING[model]
    input_cost = input_tokens * pricing["input_price_per_1m_tokens"] / 1_000_000
    output_cost = output_tokens * pricing["output_price_per_1m_tokens"] / 1_000_000
    return input_cost + output_cost
```

**When to use exceptions vs assertions:**
- **Assertions**: For preconditions, invariants, and programmer errors
- **Exceptions**: For runtime conditions outside your control (network, file I/O, user input)

## 2. Load Heavy Resources Once at Module Level
**Problem:** Repeatedly loading data in functions causes performance issues
**Solution:** Load heavy resources once at module initialization and cache them

**Why this matters:**
- Eliminates repeated I/O operations
- Improves function call performance significantly
- Makes dependencies explicit at module level
- Enables better error handling during startup

```python
# Bad: Repeated loading (expensive I/O on every call)
def get_model_pricing(model: str) -> dict[str, float]:
    pricing_data = _load_pricing_data()  # File I/O every call!
    return pricing_data[model]

def calculate_cost(model: str, tokens: int) -> float:
    pricing = get_model_pricing(model)  # Another file load!
    return tokens * pricing["price_per_token"]

# Good: Load once, use many times
MODEL_PRICING: dict[str, dict[str, float]] = _load_pricing_data()

def get_model_pricing(model: str) -> dict[str, float]:
    assert model in MODEL_PRICING, f"Model {model} not found"
    return MODEL_PRICING[model]  # Direct memory access

def calculate_cost(model: str, tokens: int) -> float:
    pricing = MODEL_PRICING[model]  # Direct access, no I/O
    return tokens * pricing["price_per_token"]

# Even better: Eliminate the getter entirely
def calculate_cost(model: str, tokens: int) -> float:
    assert model in MODEL_PRICING, f"Model {model} not found"
    return tokens * MODEL_PRICING[model]["price_per_token"]
```

**Performance impact:** Loading a 50KB JSON file 1000 times vs once:
- **Repeated loading**: ~500ms total
- **Load once**: ~0.5ms total (1000x faster)

## 3. Eliminate Deep Nesting with Early Returns and Direct Access
**Problem:** Deep nesting creates cognitive overhead and makes code hard to follow
**Solution:** Use assertions for validation, then direct operations with clear structure

**Why this matters:**
- Reduces cognitive load (fewer nested conditions to track)
- Makes the "happy path" obvious
- Easier to test and debug
- More readable and maintainable

```python
# Bad: Deep nesting (hard to follow the logic)
def get_cost_info(model: str) -> dict[str, float | None]:
    if model:
        if model.strip():
            if model in pricing:
                if "input_price_per_1m_tokens" in pricing[model]:
                    if pricing[model]["input_price_per_1m_tokens"] is not None:
                        input_price = pricing[model]["input_price_per_1m_tokens"]
                        if "output_price_per_1m_tokens" in pricing[model]:
                            if pricing[model]["output_price_per_1m_tokens"] is not None:
                                output_price = pricing[model]["output_price_per_1m_tokens"]
                                cached_price = pricing[model].get("cached_input_price_per_1m_tokens")
                                return {
                                    "input_cost_per_token": input_price / 1_000_000,
                                    "output_cost_per_token": output_price / 1_000_000,
                                    "cached_input_cost_per_token": cached_price / 1_000_000 if cached_price else None,
                                }
    return {}  # What went wrong? We don't know!

# Good: Assert preconditions, then direct operations
def get_cost_info(model: str) -> dict[str, float | None]:
    """Get cost information for a model with clear validation."""
    assert model.strip(), "Model name cannot be empty"
    assert model in MODEL_PRICING, f"Model {model} not found in pricing data"
    
    model_info = MODEL_PRICING[model]
    
    # Direct access after validation - no nesting needed
    input_price = model_info["input_price_per_1m_tokens"]
    output_price = model_info["output_price_per_1m_tokens"]
    cached_price = model_info.get("cached_input_price_per_1m_tokens")
    
    return {
        "input_cost_per_token": input_price / 1_000_000,
        "output_cost_per_token": output_price / 1_000_000,
        "cached_input_cost_per_token": cached_price / 1_000_000 if cached_price else None,
    }

# Even better: Use a dataclass for structured return
from dataclasses import dataclass

@dataclass
class ModelCostInfo:
    input_cost_per_token: float
    output_cost_per_token: float
    cached_input_cost_per_token: float | None

def get_cost_info(model: str) -> ModelCostInfo:
    assert model.strip(), "Model name cannot be empty"
    assert model in MODEL_PRICING, f"Model {model} not found"
    
    info = MODEL_PRICING[model]
    cached_price = info.get("cached_input_price_per_1m_tokens")
    
    return ModelCostInfo(
        input_cost_per_token=info["input_price_per_1m_tokens"] / 1_000_000,
        output_cost_per_token=info["output_price_per_1m_tokens"] / 1_000_000,
        cached_input_cost_per_token=cached_price / 1_000_000 if cached_price else None,
    )
```

## 4. Dynamic Data Discovery vs Hardcoded Lists
**Problem:** Hardcoded lists require manual maintenance and become stale
**Solution:** Extract available data dynamically from existing data structures

**Why this matters:**
- Eliminates maintenance burden when adding new items
- Prevents bugs from forgetting to update hardcoded lists
- Makes code more resilient to changes
- Automatically includes new data without code changes

```python
# Bad: Hardcoded file list (requires maintenance when adding providers)
PRICING_FILES = ["anthropic.json", "openai.json", "google.json"]  # Forgot "cohere.json"!

def load_all_pricing() -> dict[str, dict]:
    all_pricing = {}
    for filename in PRICING_FILES:  # Missing files won't be loaded
        file_path = PRICING_DIR / filename
        with open(file_path) as f:
            provider = filename.replace(".json", "")
            all_pricing[provider] = json.load(f)
    return all_pricing

# Good: Dynamic file discovery (automatically includes new files)
def load_all_pricing() -> dict[str, dict]:
    all_pricing = {}
    pricing_files = list(PRICING_DIR.glob("*.json"))  # Finds ALL JSON files
    
    for file_path in pricing_files:
        provider = file_path.stem  # filename without extension
        with open(file_path) as f:
            all_pricing[provider] = json.load(f)
    
    return all_pricing

# Bad: Hardcoded test models (becomes stale when models change)
def test_cost_calculation():
    test_models = [
        "claude-3-5-sonnet-20241022", 
        "gpt-4o-mini", 
        "gemini-2.0-flash"  # What about new models?
    ]
    for model in test_models:
        cost = calculate_cost(model, 1000, 500)
        assert cost > 0, f"Cost should be positive for {model}"

# Good: Use available models from loaded data
def test_cost_calculation():
    test_models = list(MODEL_PRICING.keys())  # Tests ALL available models
    
    for model in test_models:
        cost = calculate_cost(model, 1000, 500)
        assert cost > 0, f"Cost should be positive for {model}"

# Even better: Use sampling for large datasets
import random

def test_cost_calculation():
    all_models = list(MODEL_PRICING.keys())
    # Test a representative sample if there are many models
    test_models = random.sample(all_models, min(10, len(all_models)))
    
    for model in test_models:
        cost = calculate_cost(model, 1000, 500)
        assert cost > 0, f"Cost should be positive for {model}"
```

**Real-world impact:** When Quinn added support for new LLM providers, the dynamic discovery approach automatically included them in tests and processing without any code changes.

## 5. Use Named Tuples for Structured Function Returns
**Problem:** Anonymous tuples and dictionaries create unclear, error-prone interfaces
**Solution:** Use named tuples or dataclasses for self-documenting, structured return values

**Why this matters:**
- Self-documenting code (field names explain what each value represents)
- Type safety and IDE support (autocomplete, type checking)
- Prevents argument order mistakes
- Easy to extend with additional fields
- Immutable by default (prevents accidental modification)

```python
# Bad: Anonymous tuple return (unclear what each value represents)
def _calculate_usage_metrics(result, config) -> tuple[int, float]:
    """Calculate token usage and cost from result."""
    tokens_used = (usage.request_tokens or 0) + (usage.response_tokens or 0)
    cost_usd = calculate_cost(model=config.model, input_tokens=..., output_tokens=...)
    return tokens_used, cost_usd

# Usage is unclear and error-prone
tokens, cost = _calculate_usage_metrics(result, config)  # Which is which?
cost, tokens = _calculate_usage_metrics(result, config)  # Oops! Wrong order

# Also bad: Dictionary return (mutable, no type safety)
def _calculate_usage_metrics(result, config) -> dict[str, int | float]:
    return {
        "tokens": tokens_used,
        "cost": cost_usd,  # Typos in keys are runtime errors
    }

# Usage requires magic strings
metrics = _calculate_usage_metrics(result, config)
print(f"Cost: {metrics['cost']}")  # Typo-prone, no autocomplete

# Good: Named tuple with clear field names and detailed breakdown
from typing import NamedTuple

class UsageMetrics(NamedTuple):
    """Detailed usage metrics breakdown."""
    input_tokens: int
    output_tokens: int
    cached_tokens: int
    total_tokens: int
    total_cost_usd: float

def _calculate_usage_metrics(result, config) -> UsageMetrics:
    """Calculate detailed token usage and cost breakdown from result."""
    usage = result.usage()
    input_tokens = usage.request_tokens or 0
    output_tokens = usage.response_tokens or 0
    
    # Extract cached tokens from details if available
    cached_tokens = 0
    if usage.details:
        cached_keys = ['cache_read_input_tokens', 'cached_tokens', 'cache_tokens']
        for key in cached_keys:
            if key in usage.details:
                cached_tokens = usage.details[key]
                break
    
    total_tokens = usage.total_tokens or (input_tokens + output_tokens)
    cost_usd = calculate_cost(model=config.model, input_tokens=input_tokens, output_tokens=output_tokens)
    
    return UsageMetrics(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cached_tokens=cached_tokens,
        total_tokens=total_tokens,
        total_cost_usd=cost_usd
    )

# Usage is self-documenting and type-safe
metrics = _calculate_usage_metrics(result, config)
print(f"Used {metrics.input_tokens} input tokens, {metrics.output_tokens} output tokens")
print(f"Cached: {metrics.cached_tokens}, Total cost: ${metrics.total_cost_usd:.4f}")

# Alternative: Use dataclass for mutable data or methods
from dataclasses import dataclass

@dataclass(frozen=True)  # frozen=True makes it immutable like NamedTuple
class UsageMetrics:
    """Detailed usage metrics breakdown."""
    input_tokens: int
    output_tokens: int
    cached_tokens: int
    total_tokens: int
    total_cost_usd: float
    
    @property
    def cost_per_token(self) -> float:
        """Calculate cost per token."""
        return self.total_cost_usd / self.total_tokens if self.total_tokens > 0 else 0.0
    
    def format_summary(self) -> str:
        """Format a human-readable summary."""
        return (f"Tokens: {self.input_tokens} -> {self.output_tokens} "
                f"(cached: {self.cached_tokens}), Cost: ${self.total_cost_usd:.4f}")
```

**When to use each approach:**
- **NamedTuple**: Simple data containers, immutable, lightweight
- **Dataclass**: Need methods, default values, or mutable fields
- **Regular dict**: Only for truly dynamic data where keys aren't known at design time


# Database Transaction Safety: Validate Before Commit

**Problem:** Committing transactions before validating success can corrupt data and make errors unrecoverable  
**Solution:** Always execute operations, validate success, then commit - enabling rollback on failure

**Why this matters:**
- Maintains data integrity by preventing invalid commits
- Enables error recovery through transaction rollback
- Follows fail-fast principle with clear error messages
- Prevents silent failures that cause downstream issues

## The Pattern: Execute → Validate → Commit

```python
# Bad: Commit before validation (irreversible damage)
conn.commit()
assert cursor.rowcount == 1, (
    f"Failed to create conversation {conversation.id}"
)  # Too late - data already committed!

# Good: Validate before commit (safe and recoverable)
logger.info("SQL: %s | Params: %s", sql.strip(), params)
cursor.execute(sql, params)
assert cursor.rowcount == 1, (
    f"Failed to insert conversation {conversation.id}"
)  # Check success first
conn.commit()  # Only commit if validation passes
```

## Key Benefits

**Transaction Safety**
- Failed validation can trigger rollback before data corruption
- Maintains ACID compliance and database consistency
- Prevents partial operations from being permanently saved

**Fail Fast Principle**
- Assertions fail immediately with specific error messages
- Stops execution at the exact point of failure
- No silent failures or defensive masking of real problems

**Debugging Support**
- SQL logging helps trace execution flow
- Clear error messages identify exactly what failed
- Transaction boundaries are explicit and testable

## Complete Pattern with Assertions

```python
def insert_conversation(conn, cursor, conversation):
    """Insert conversation with proper transaction safety."""
    sql = "INSERT INTO conversations (id, title, created_at) VALUES (?, ?, ?)"
    params = (conversation.id, conversation.title, conversation.created_at)
    
    logger.info("SQL: %s | Params: %s", sql.strip(), params)
    cursor.execute(sql, params)
    
    # Validate success before committing - fail fast with clear message
    assert cursor.rowcount == 1, (
        f"Failed to insert conversation {conversation.id}: "
        f"expected 1 row affected, got {cursor.rowcount}"
    )
    
    conn.commit()
    logger.info("Successfully inserted conversation %s", conversation.id)
```

## When to Use This Pattern

**Always use for:**
- INSERT/UPDATE/DELETE operations where row count matters
- Multi-step transactions that must complete atomically
- Operations where data integrity is critical

**Validation techniques:**
- `cursor.rowcount` for affected row count validation
- `cursor.lastrowid` for auto-generated ID verification
- Custom queries to verify expected state changes

**Assertion guidelines:**
- Use assertions for database operation validation (programmer errors)
- Let real database exceptions (network, permissions, constraints) bubble up naturally
- Provide specific, actionable error messages in assertions

This pattern ensures data integrity by validating success before making changes permanent, enabling safe recovery when operations fail.