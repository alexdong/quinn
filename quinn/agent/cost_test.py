"""Test cost calculation functions."""

import pytest

from .cost import (
    calculate_cost,
    estimate_completion_cost,
    get_cost_per_token,
    get_model_cost_info,
    ModelCostInfo,
    CompletionCostEstimate,
    get_supported_models,
)


def test_get_model_cost_info() -> None:
    """Test getting model cost information."""
    # Test with known models from our pricing data
    test_models = [
        "gemini-2.5-flash-exp",
        "gemini-2.0-flash", 
        "gpt-4o-mini",
        "claude-3-5-sonnet-20241022"
    ]
    
    for model in test_models:
        cost_info = get_model_cost_info(model)
        assert isinstance(cost_info, ModelCostInfo)
        assert cost_info.input_cost_per_token >= 0.0
        assert cost_info.output_cost_per_token >= 0.0


def test_calculate_cost() -> None:
    """Test cost calculation."""
    # Test with known paid model (not free)
    model = "gpt-4o-mini"
    cost = calculate_cost(
        model=model,
        input_tokens=1000,
        output_tokens=500,
    )
    
    assert isinstance(cost, float)
    assert cost >= 0.0
    
    # Cost should be proportional to token usage
    higher_cost = calculate_cost(
        model=model, 
        input_tokens=2000,
        output_tokens=1000,
    )
    assert higher_cost > cost


def test_get_cost_per_token() -> None:
    """Test getting cost per token."""
    model = "gpt-4o-mini"
    input_cost = get_cost_per_token(model, "input")
    output_cost = get_cost_per_token(model, "output")
    cached_input_cost = get_cost_per_token(model, "cached_input")
    
    assert isinstance(input_cost, float)
    assert isinstance(output_cost, float)
    assert isinstance(cached_input_cost, float)
    assert input_cost >= 0.0
    assert output_cost >= 0.0
    assert cached_input_cost >= 0.0


def test_estimate_completion_cost() -> None:
    """Test completion cost estimation."""
    estimate = estimate_completion_cost(
        model="gpt-4o-mini",
        prompt="This is a test prompt for cost estimation.",
        max_tokens=100,
    )
    
    assert isinstance(estimate, CompletionCostEstimate)
    assert estimate.estimated_total_cost >= 0.0
    assert estimate.estimated_input_tokens >= 0
    assert estimate.estimated_output_tokens >= 0
    assert estimate.input_cost_per_token >= 0.0
    assert estimate.output_cost_per_token >= 0.0


def test_get_supported_models() -> None:
    """Test getting supported models list."""
    models = get_supported_models()
    assert isinstance(models, list)
    assert len(models) > 0
    
    # Should include our known models
    expected_models = [
        "gpt-4o-mini",
        "claude-3-5-sonnet-20241022",
        "gemini-2.0-flash",
        "gemini-2.5-flash-exp"
    ]
    
    for model in expected_models:
        assert model in models


def test_fallback_pricing() -> None:
    """Test fallback pricing for unknown models."""
    unknown_model = "unknown-test-model"
    
    # Should raise assertion error for unknown model
    with pytest.raises(AssertionError, match="not found in pricing data"):
        get_model_cost_info(unknown_model)


def test_free_model_pricing() -> None:
    """Test that free experimental models have zero cost."""
    free_model = "gemini-2.5-flash-exp"
    cost_info = get_model_cost_info(free_model)

    assert cost_info.input_cost_per_token == 0.0
    assert cost_info.output_cost_per_token == 0.0
    
    # Cost calculation should be zero
    cost = calculate_cost(free_model, 1000, 500)
    assert cost == 0.0


def test_cached_input_cost() -> None:
    """Test cost calculation with cached input tokens."""
    model = "gpt-4o-mini"
    
    # Test with cached input tokens
    cost_with_cache = calculate_cost(
        model=model,
        input_tokens=500,
        output_tokens=300,
        cached_input_tokens=1000,
    )
    
    # Test without cached input tokens
    cost_without_cache = calculate_cost(
        model=model,
        input_tokens=1500,  # 500 + 1000
        output_tokens=300,
    )
    
    assert isinstance(cost_with_cache, float)
    assert cost_with_cache >= 0.0
    # Cached cost should typically be less than or equal to regular cost
    assert cost_with_cache <= cost_without_cache


def test_calculate_cost_validation() -> None:
    """Test cost calculation input validation."""
    with pytest.raises(AssertionError, match="Model name cannot be empty"):
        calculate_cost("", 100, 50)
        
    with pytest.raises(AssertionError, match="Input tokens must be non-negative"):
        calculate_cost("gemini-2.5-flash-exp", -1, 50)
        
    with pytest.raises(AssertionError, match="Output tokens must be non-negative"):
        calculate_cost("gemini-2.5-flash-exp", 100, -1)
    
    with pytest.raises(AssertionError, match="Cached input tokens must be non-negative"):
        calculate_cost("gpt-4o-mini", 100, 50, -1)


if __name__ == "__main__":
    # Run all tests
    print("🧪 Running cost calculation tests...")
    
    test_get_model_cost_info()
    test_calculate_cost()
    test_get_cost_per_token() 
    test_estimate_completion_cost()
    test_get_supported_models()
    test_fallback_pricing()
    test_free_model_pricing()
    test_cached_input_cost()
    test_calculate_cost_validation()
    
    print("✅ All cost calculation tests passed!")
    
    # Show supported models
    models = get_supported_models()
    print(f"\n📋 Supported models ({len(models)}):")
    for model in models:
        print(f"  - {model}")
    
    # Compare costs across models
    print(f"\n💰 Cost comparison for 1000 input + 500 output tokens:")
    test_models = ["gpt-4o-mini", "claude-3-5-sonnet-20241022", "gemini-2.0-flash", "gemini-2.5-flash-exp"]
    
    for model in test_models:
        cost = calculate_cost(model, 1000, 500)
        print(f"  {model}: ${cost:.6f}")
    
    # Example estimation
    print(f"\n🔮 Cost estimation example:")
    model = "gpt-4o-mini"
    estimate = estimate_completion_cost(
        model,
        "Write a short story about a robot learning to paint.",
        max_tokens=200,
    )
    print(f"  Model: {model}")
    print(f"  Estimated cost: ${estimate.estimated_total_cost:.6f}")
    print(f"  Input tokens: {estimate.estimated_input_tokens}")
    print(f"  Output tokens: {estimate.estimated_output_tokens}")
    
    print(f"\n🧪 Cost calculation tests completed!")

def test_main_demo_function() -> None:
    """Test the main demo function for coverage."""
    from unittest.mock import patch
    from io import StringIO
    from quinn.agent.cost import main
    
    # Capture stdout to avoid cluttering test output
    captured_output = StringIO()
    with patch("sys.stdout", captured_output):
        main()
    
    output = captured_output.getvalue()
    assert "Cost Calculation Demo" in output
    assert "Supported models" in output



def test_demo_functions_cache_savings_and_errors() -> None:
    """Test demo functions to cover cache savings and error handling."""
    from unittest.mock import patch
    from io import StringIO
    from quinn.agent.cost import _demo_model_costs, _demo_cost_estimation
    
    # Test cache savings calculation (lines 188-190)
    captured_output = StringIO()
    with patch("sys.stdout", captured_output):
        # Use a model with cached pricing to trigger savings calculation
        _demo_model_costs("claude-3-5-sonnet-20241022", 1000, 500, 2000)
    
    output = captured_output.getvalue()
    # Should show cache savings if the model supports it
    assert "claude-3-5-sonnet-20241022" in output
    
    # Test error handling in demo (lines 217-218)
    captured_output = StringIO()
    with patch("sys.stdout", captured_output):
        with patch("quinn.agent.cost.estimate_completion_cost", side_effect=Exception("Test error")):
            _demo_cost_estimation(["gpt-4o-mini"])
    
    output = captured_output.getvalue()
    assert "Error: Test error" in output

