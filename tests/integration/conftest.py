"""Pytest fixtures for integration tests."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from quinn.agent.core import create_agent, generate_response
from quinn.models import AgentConfig, Message


@pytest.fixture
def mock_api_keys():
    """Mock API keys for testing without real API calls."""
    with patch.dict("os.environ", {
        "OPENAI_API_KEY": "test-openai-key",
        "ANTHROPIC_API_KEY": "test-anthropic-key", 
        "GEMINI_API_KEY": "test-gemini-key"
    }):
        yield


@pytest.fixture
def agent_config():
    """Provide a test agent configuration."""
    return AgentConfig(
        model="gpt-4o-mini",
        temperature=0.7,
        max_tokens=1000,
        timeout_seconds=30,
        max_retries=2
    )


@pytest.fixture
def sample_message():
    """Provide a sample message for testing."""
    return Message(
        user_content="Hello, I need help with a Python problem",
        conversation_id="test-conv-123",
        system_prompt="You are a helpful assistant"
    )


@pytest.fixture
def conversation_history():
    """Provide sample conversation history."""
    return [
        Message(
            user_content="Hi there",
            assistant_content="Hello! How can I help you today?",
            conversation_id="test-conv-123"
        ),
        Message(
            user_content="I'm working on a Python project",
            assistant_content="That's great! What kind of Python project are you working on?",
            conversation_id="test-conv-123"
        )
    ]


@pytest.fixture
def temp_log_file():
    """Provide a temporary log file for testing."""
    log_file = Path(tempfile.mktemp(suffix=".log"))
    yield log_file
    
    # Cleanup
    if log_file.exists():
        log_file.unlink()


@pytest.fixture
def integration_test_data():
    """Provide comprehensive test data for integration tests."""
    return {
        "test_problems": [
            "My Python code is running slowly and I don't know why",
            "I'm getting a 404 error on my website", 
            "Should I use React or Vue for my new project?",
            "How do I optimize this SQL query?",
            "My Docker container won't start"
        ],
        "expected_question_patterns": [
            "what", "how", "can you", "tell me", "describe", "explain", "?"
        ],
        "avoid_solution_patterns": [
            "solution", "fix", "do this", "run this command", "the answer is"
        ]
    }


@pytest.fixture
def mock_successful_response():
    """Mock a successful API response."""
    return {
        "content": "That's an interesting problem! Can you tell me more about what specific symptoms you're observing? What makes you think the code is running slowly?",
        "usage": {
            "total_tokens": 45,
            "prompt_tokens": 25,
            "completion_tokens": 20
        },
        "model": "gpt-4o-mini"
    }


@pytest.fixture
def mock_error_response():
    """Mock an API error response."""
    return {
        "error": {
            "message": "Rate limit exceeded",
            "type": "rate_limit_error",
            "code": "rate_limit_exceeded"
        }
    }


@pytest.fixture
def performance_thresholds():
    """Define performance thresholds for integration tests."""
    return {
        "max_response_time_ms": 5000,  # 5 seconds
        "max_tokens_per_response": 500,
        "max_cost_per_response_usd": 0.01,
        "min_response_length": 10
    }