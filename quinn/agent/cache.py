"""Response caching functionality."""

import hashlib

from quinn.models import Message

# Simple in-memory cache for now
_response_cache: dict[str, Message] = {}


def get_cached_response(prompt_hash: str) -> Message | None:
    """Retrieve cached response if available."""
    assert prompt_hash.strip(), "Prompt hash cannot be empty"
    return _response_cache.get(prompt_hash)


def cache_response(prompt_hash: str, response: Message) -> None:
    """Cache response for future use."""
    assert prompt_hash.strip(), "Prompt hash cannot be empty"
    assert isinstance(response, Message), "Response must be Message instance"

    _response_cache[prompt_hash] = response


def generate_prompt_hash(user_input: str, system_prompt: str, model: str) -> str:
    """Generate hash for prompt caching."""
    assert user_input.strip(), "User input cannot be empty"
    assert system_prompt.strip(), "System prompt cannot be empty"
    assert model.strip(), "Model cannot be empty"

    content = f"{user_input}|{system_prompt}|{model}"
    return hashlib.sha256(content.encode()).hexdigest()


def clear_cache() -> None:
    """Clear the response cache."""
    _response_cache.clear()
