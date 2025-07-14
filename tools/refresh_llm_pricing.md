# LLM Pricing Data Refresh Prompt

Fetch the latest pricing for these models from their official provider websites and create/update JSON files in `quinn/agent/pricing/`.

Include both regular and cached input pricing for all models.

## Providers and Models

### 1. OpenAI (https://platform.openai.com/docs/pricing)
Create `openai.json` with:
- gpt-4o-mini
- o3
- o4-mini  
- gpt-4.1
- gpt-4.1-mini
- gpt-4.1-nano

### 2. Anthropic (https://www.anthropic.com/pricing)
Create `anthropic.json` with:
- claude-3-5-sonnet-20241022
- claude-opus-4-20250514
- claude-sonnet-4
- claude-haiku-3.5

### 3. Google (https://ai.google.dev/gemini-api/docs/pricing)
Create `google.json` with:
- gemini-2.0-flash
- gemini-2.5-flash-exp
- gemini-2.5-pro
- gemini-2.5-flash

## JSON Schema

Each JSON file should include:
- `last_updated`: current date (YYYY-MM-DD format)
- `source_url`: provider pricing page URL
- `models`: object with model names as keys, each containing:
  - `input_price_per_1m_tokens`: price per 1M input tokens (USD)
  - `output_price_per_1m_tokens`: price per 1M output tokens (USD)
  - `cached_input_price_per_1m_tokens`: price per 1M cached input tokens (USD, or `null` if not supported)
  - `notes`: optional field for additional context about pricing or model features

## Requirements

- Use exact model names as they appear in our `config.py` file or as documented by the provider
- All prices must be in USD
- Include cached pricing when available from the provider
- Use `null` for `cached_input_price_per_1m_tokens` when the model doesn't support caching
- Verify pricing accuracy by cross-referencing multiple sources when possible
- Include any relevant notes about pricing tiers, context windows, or special features