"""Test response caching functionality."""

import pytest

from quinn.models import AgentResponse

from .cache import cache_response, clear_cache, generate_prompt_hash, get_cached_response


def test_generate_prompt_hash() -> None:
    """Test prompt hash generation."""
    hash1 = generate_prompt_hash("user input", "system prompt", "gemini/gemini-2.5-flash-exp")
    hash2 = generate_prompt_hash("user input", "system prompt", "gemini/gemini-2.5-flash-exp")
    hash3 = generate_prompt_hash("different input", "system prompt", "gemini/gemini-2.5-flash-exp")
    
    # Same inputs should produce same hash
    assert hash1 == hash2
    
    # Different inputs should produce different hash
    assert hash1 != hash3
    
    # Hash should be a string
    assert isinstance(hash1, str)
    assert len(hash1) > 0


def test_generate_prompt_hash_validation() -> None:
    """Test prompt hash generation validation."""
    with pytest.raises(AssertionError, match="User input cannot be empty"):
        generate_prompt_hash("", "system prompt", "model")
    
    with pytest.raises(AssertionError, match="System prompt cannot be empty"):
        generate_prompt_hash("user input", "", "model")
    
    with pytest.raises(AssertionError, match="Model cannot be empty"):
        generate_prompt_hash("user input", "system prompt", "")


def test_cache_operations() -> None:
    """Test caching and retrieval operations."""
    # Clear cache first
    clear_cache()
    
    # Test cache miss
    hash_key = "test_hash_123"
    result = get_cached_response(hash_key)
    assert result is None
    
    # Create a test response
    response = AgentResponse(
        content="Test response",
        conversation_id="conv-123",
        message_id="msg-456",
        model_used="gemini/gemini-2.5-flash-exp",
        prompt_version="v1.0",
    )
    
    # Cache the response
    cache_response(hash_key, response)
    
    # Test cache hit
    cached = get_cached_response(hash_key)
    assert cached is not None
    assert cached.content == "Test response"
    assert cached.conversation_id == "conv-123"
    assert cached.message_id == "msg-456"
    
    # Clear cache and test miss again
    clear_cache()
    result = get_cached_response(hash_key)
    assert result is None


def test_cache_validation() -> None:
    """Test cache operation validation."""
    response = AgentResponse(
        content="Test response",
        conversation_id="conv-123", 
        message_id="msg-456",
        model_used="gemini/gemini-2.5-flash-exp",
        prompt_version="v1.0",
    )
    
    with pytest.raises(AssertionError, match="Prompt hash cannot be empty"):
        cache_response("", response)
    
    with pytest.raises(AssertionError, match="Prompt hash cannot be empty"):
        get_cached_response("")
    
    with pytest.raises(AssertionError, match="Response must be AgentResponse instance"):
        cache_response("hash", "not-a-response")  # type: ignore


if __name__ == "__main__":
    pytest.main([__file__, "-v"])