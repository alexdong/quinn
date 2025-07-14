"""Test cost calculation functions."""

import pytest

from .cost import calculate_cost, estimate_completion_cost, get_cost_per_token, get_model_cost_info


def test_get_model_cost_info() -> None:
    """Test getting model cost information."""
    # Test with gemini model
    cost_info = get_model_cost_info("gemini/gemini-2.5-flash-exp")
    assert isinstance(cost_info, dict)
    assert "input_cost_per_token" in cost_info
    assert "output_cost_per_token" in cost_info
    assert cost_info["input_cost_per_token"] >= 0.0
    assert cost_info["output_cost_per_token"] >= 0.0


def test_calculate_cost() -> None:
    """Test cost calculation."""
    # Test with known model
    cost = calculate_cost(
        model="gemini/gemini-2.5-flash-exp",
        input_tokens=1000,
        output_tokens=500,
    )
    
    assert isinstance(cost, float)
    assert cost >= 0.0
    
    # Cost should be proportional to token usage
    higher_cost = calculate_cost(
        model="gemini/gemini-2.5-flash-exp", 
        input_tokens=2000,
        output_tokens=1000,
    )
    assert higher_cost > cost


def test_get_cost_per_token() -> None:
    """Test getting cost per token."""
    input_cost = get_cost_per_token("gemini/gemini-2.5-flash-exp", "input")
    output_cost = get_cost_per_token("gemini/gemini-2.5-flash-exp", "output")
    
    assert isinstance(input_cost, float)
    assert isinstance(output_cost, float)
    assert input_cost >= 0.0
    assert output_cost >= 0.0


def test_estimate_completion_cost() -> None:
    """Test completion cost estimation."""
    estimate = estimate_completion_cost(
        model="gemini/gemini-2.5-flash-exp",
        prompt="This is a test prompt for cost estimation.",
        max_tokens=100,
    )
    
    assert isinstance(estimate, dict)
    required_keys = [
        "estimated_total_cost",
        "estimated_input_tokens", 
        "estimated_output_tokens",
        "input_cost_per_token",
        "output_cost_per_token",
    ]
    
    for key in required_keys:
        assert key in estimate
        assert isinstance(estimate[key], (int, float))
        assert estimate[key] >= 0.0


def test_calculate_cost_validation() -> None:
    """Test cost calculation input validation."""
    with pytest.raises(AssertionError, match="Model name cannot be empty"):
        calculate_cost("", 100, 50)
        
    with pytest.raises(AssertionError, match="Input tokens must be non-negative"):
        calculate_cost("gemini/gemini-2.5-flash-exp", -1, 50)
        
    with pytest.raises(AssertionError, match="Output tokens must be non-negative"):
        calculate_cost("gemini/gemini-2.5-flash-exp", 100, -1)


if __name__ == "__main__":
    # Run basic tests
    test_get_model_cost_info()
    test_calculate_cost()
    test_get_cost_per_token() 
    test_estimate_completion_cost()
    
    print("✅ All cost calculation tests passed!")
    
    # Print some example costs
    model = "gemini/gemini-2.5-flash-exp"
    cost_info = get_model_cost_info(model)
    
    print(f"\n📊 Cost information for {model}:")
    print(f"  Input cost per token: ${cost_info['input_cost_per_token']:.8f}")
    print(f"  Output cost per token: ${cost_info['output_cost_per_token']:.8f}")
    
    # Example calculation
    cost = calculate_cost(model, 1000, 500)
    print(f"\n💰 Cost for 1000 input + 500 output tokens: ${cost:.6f}")
    
    # Example estimation
    estimate = estimate_completion_cost(
        model,
        "Write a short story about a robot learning to paint.",
        max_tokens=200,
    )
    print(f"\n🔮 Estimated cost for completion: ${estimate['estimated_total_cost']:.6f}")
    print(f"  Estimated input tokens: {estimate['estimated_input_tokens']}")
    print(f"  Estimated output tokens: {estimate['estimated_output_tokens']}")