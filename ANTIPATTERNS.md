# Code Smells

Code smells are patterns that indicate potential issues in code quality, maintainability, or performance. They are not necessarily bugs but can lead to problems if not addressed. Here are some common code smells and how to refactor them for better performance and maintainability.

## 1. Replace Defensive try/except with Assertions
**Instead of:** Wrapping every operation in try/except blocks
**Do:** Use assertions for input validation and contract enforcement
```python
# Bad: Defensive exception handling
try:
    if model in MODEL_PRICING:
        return MODEL_PRICING[model]
    else:
        raise ValueError(f"Model {model} not found")
except Exception as e:
    logger.error(f"Error: {e}")
    return None

# Good: Clear assertions with descriptive messages
assert model.strip(), "Model name cannot be empty"
assert model in MODEL_PRICING, f"Model {model} not found in pricing data"
return MODEL_PRICING[model]
```

## 2. Load Heavy Resources Once at Module Level
**Instead of:** Loading data repeatedly in function calls
**Do:** Load once and cache at module initialization
```python
# Bad: Repeated loading
def get_model_info(model):
    pricing_data = _load_pricing_data()  # Loads every call
    return pricing_data[model]

# Good: Load once, use many times
MODEL_PRICING: dict[str, dict[str, float]] = _load_pricing_data()

def get_model_info(model):
    return MODEL_PRICING[model]  # Direct access
```

## 3. Eliminate Deep Nesting with Early Returns and Direct Access
**Instead of:** Nested if/else chains and complex error handling
**Do:** Use assertions for validation, then direct operations
```python
# Bad: Deep nesting
def get_cost_info(model):
    if model:
        if model in pricing:
            if "input_price" in pricing[model]:
                if pricing[model]["input_price"] is not None:
                    return {
                        "input": pricing[model]["input_price"] / 1_000_000,
                        # ... more nesting
                    }

# Good: Assert preconditions, then direct operations  
def get_cost_info(model):
    assert model.strip(), "Model name cannot be empty"
    assert model in MODEL_PRICING, f"Model {model} not found"
    
    model_info = MODEL_PRICING[model]
    cached_price = model_info["cached_input_price_per_1m_tokens"]
    
    return {
        "input_cost_per_token": model_info["input_price_per_1m_tokens"] / 1_000_000,
        "cached_input_cost_per_token": cached_price / 1_000_000 if cached_price else None,
    }
```

## 4. Dynamic Data Discovery vs Hardcoded Lists
**Instead of:** Maintaining hardcoded lists that require manual updates
**Do:** Extract available data from existing data structures
```python
# Bad: Hardcoded file list (requires maintenance when adding providers)
PRICING_FILES = ["anthropic.json", "openai.json", "google.json"]
for filename in PRICING_FILES:
    file_path = PRICING_DIR / filename
    # Process file...

# Good: Dynamic file discovery (automatically includes new files)
pricing_files = [f.name for f in PRICING_DIR.glob("*.json")]
for filename in pricing_files:
    file_path = PRICING_DIR / filename
    # Process file...

# Bad: Hardcoded test models (requires maintenance when models change)
test_models = ["claude-3-5-sonnet-20241022", "gpt-4o-mini", "gemini-2.0-flash"]
for model in test_models:
    # Run tests...

# Good: Use available models from loaded data (automatically includes all models)
test_models = get_supported_models()  # Returns list(MODEL_PRICING.keys())
for model in test_models:
    # Run tests...
```
