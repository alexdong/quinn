"""Pytest fixtures for end-to-end tests."""

import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace for e2e tests."""
    workspace = Path(tempfile.mkdtemp(prefix="quinn_e2e_"))
    
    # Create basic directory structure
    (workspace / "logs").mkdir()
    (workspace / "data").mkdir()
    (workspace / "config").mkdir()
    
    yield workspace
    
    # Cleanup
    import shutil
    if workspace.exists():
        shutil.rmtree(workspace)


@pytest.fixture
def mock_email_data():
    """Provide mock email data for testing."""
    return {
        "from": "user@example.com",
        "to": "quinn@example.com",
        "subject": "Help with Python debugging",
        "body": "Hi Quinn, I'm having trouble with my Python code. It's running slowly and I can't figure out why. Can you help me think through this?",
        "message_id": "test-message-123",
        "thread_id": "test-thread-456"
    }


@pytest.fixture
def mock_cli_input():
    """Provide mock CLI input for testing."""
    return [
        "quinn -n 'My website is down and I need help debugging'",
        "quinn -c 123",
        "quinn -l",
        "echo 'Database connection failing' | quinn"
    ]


@pytest.fixture
def e2e_test_scenarios():
    """Provide comprehensive e2e test scenarios."""
    return [
        {
            "name": "new_conversation_cli",
            "description": "Start new conversation via CLI",
            "input": "My React app won't compile",
            "expected_outputs": [
                "questions about the error",
                "clarification requests",
                "no direct solutions"
            ]
        },
        {
            "name": "continue_conversation",
            "description": "Continue existing conversation",
            "input": "The error says 'Module not found'",
            "context": "Previous discussion about React compilation",
            "expected_outputs": [
                "follow-up questions",
                "deeper investigation prompts"
            ]
        },
        {
            "name": "email_thread_processing",
            "description": "Process email thread with history",
            "input": "Thanks for the questions. Here are the details...",
            "context": "Email thread with 3 previous exchanges",
            "expected_outputs": [
                "acknowledgment of provided details",
                "next level questions",
                "synthesis of conversation"
            ]
        }
    ]


@pytest.fixture
def performance_monitoring():
    """Monitor performance during e2e tests."""
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.metrics = {}
        
        def start(self, operation_name: str):
            self.start_time = time.time()
            self.metrics[operation_name] = {"start": self.start_time}
        
        def end(self, operation_name: str):
            if operation_name in self.metrics:
                end_time = time.time()
                self.metrics[operation_name]["end"] = end_time
                self.metrics[operation_name]["duration"] = end_time - self.metrics[operation_name]["start"]
        
        def get_duration(self, operation_name: str) -> float:
            return self.metrics.get(operation_name, {}).get("duration", 0.0)
        
        def assert_performance(self, operation_name: str, max_duration: float):
            duration = self.get_duration(operation_name)
            assert duration <= max_duration, f"{operation_name} took {duration:.2f}s, expected <= {max_duration}s"
    
    return PerformanceMonitor()


@pytest.fixture
def mock_external_services():
    """Mock external services for e2e testing."""
    class MockServices:
        def __init__(self):
            self.email_service_calls = []
            self.ai_service_calls = []
            self.database_calls = []
        
        def mock_email_send(self, to: str, subject: str, body: str):
            self.email_service_calls.append({
                "to": to,
                "subject": subject, 
                "body": body,
                "timestamp": time.time()
            })
            return {"status": "sent", "message_id": f"mock-{len(self.email_service_calls)}"}
        
        def mock_ai_response(self, prompt: str):
            self.ai_service_calls.append({
                "prompt": prompt,
                "timestamp": time.time()
            })
            return {
                "response": "That's an interesting question! Can you tell me more about...",
                "tokens": 25,
                "cost": 0.001
            }
        
        def get_call_count(self, service: str) -> int:
            if service == "email":
                return len(self.email_service_calls)
            elif service == "ai":
                return len(self.ai_service_calls)
            elif service == "database":
                return len(self.database_calls)
            return 0
    
    return MockServices()


@pytest.fixture
def e2e_config():
    """Provide configuration for e2e tests."""
    return {
        "timeouts": {
            "cli_response": 10.0,  # seconds
            "email_processing": 15.0,
            "ai_generation": 30.0
        },
        "limits": {
            "max_conversation_length": 50,
            "max_response_tokens": 1000,
            "max_cost_per_conversation": 0.50
        },
        "test_data": {
            "sample_problems": [
                "Database connection timeout",
                "CSS layout not working",
                "Python import error",
                "Docker build failing",
                "API returning 500 errors"
            ]
        }
    }


@pytest.fixture
def cleanup_e2e_artifacts():
    """Clean up artifacts created during e2e tests."""
    artifacts = []
    
    def register_artifact(path: Path):
        artifacts.append(path)
    
    yield register_artifact
    
    # Cleanup all registered artifacts
    for artifact in artifacts:
        if artifact.exists():
            if artifact.is_file():
                artifact.unlink()
            elif artifact.is_dir():
                import shutil
                shutil.rmtree(artifact)