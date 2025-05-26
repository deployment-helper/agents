import os
import pytest
from unittest.mock import patch


@pytest.fixture(autouse=True)
def mock_env_variables():
    """
    Fixture to mock environment variables for testing
    This avoids tests relying on actual environment variables being set
    """
    env_vars = {
        "LLM_PROVIDER": "openai",
        "LLM_MODEL": "gpt-4-test",
        "LLM_API_KEY": "test-api-key",
        "LLM_TEMPERATURE": "0.5",
        "VIDEO_API_BASE_URL": "https://test-api.example.com",
        "VIDEO_API_KEY": "test-video-key",
        "SERVER_API_KEY": "test-server-key",
        "TEMP_FILE_PATH": "/tmp/test/temp",
        "MCQ_FILES_PATH": "/tmp/test/mcq",
        "AWS_ACCESS_KEY": "test-aws-key",
        "AWS_SECRET_KEY": "test-aws-secret"
    }
    
    with patch.dict(os.environ, env_vars): 
        yield


@pytest.fixture
def sample_pdf_path():
    """Fixture to provide a sample PDF path for testing"""
    return "/tmp/test_sample.pdf"


@pytest.fixture
def sample_image_path():
    """Fixture to provide a sample image path for testing"""
    return "/tmp/test_sample.jpg"


@pytest.fixture
def sample_text_path():
    """Fixture to provide a sample text file path for testing"""
    return "/tmp/test_sample.txt"


@pytest.fixture
def sample_document_text():
    """Fixture to provide sample document text for MCQ generation"""
    return """
    This is a sample document text for testing MCQ generation.
    It contains information about testing and Python programming.
    
    Python is a high-level, interpreted programming language.
    It was created by Guido van Rossum and first released in 1991.
    Python has a design philosophy that emphasizes code readability.
    
    Testing is an important part of software development.
    Unit testing focuses on testing individual components or functions.
    Integration testing focuses on testing how components work together.
    """
