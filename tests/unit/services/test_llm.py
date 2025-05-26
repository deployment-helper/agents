import pytest
from unittest.mock import patch, MagicMock
from app.services.llm import LLMService


class TestLLMService:
    """
    Unit tests for the LLMService class
    """

    def test_init_with_openai(self):
        """Test initialization with OpenAI provider"""
        with on('app.services.llm.ChatOpenAI') as mock_chat_openai:
            mock_model = MagicMock()
            mock_chat_openai.return_value = mock_model
            
            service = LLMService(provider_name="openai", model_name="gpt-4", api_key="fake-key")
            
            assert service.provider_name == "openai"
            assert service.model_name == "gpt-4"
            assert service.api_key == "fake-key"
            assert service.model == mock_model
            
            # Verify the model was initialized with the correct parameters
            mock_chat_openai.assert_called_once_with(
                model_name="gpt-4", 
                openai_api_key="fake-key"
            )

    def test_init_with_unsupported_provider(self):
        """Test initialization with an unsupported provider"""
        with pytest.raises(ValueError) as excinfo:
            LLMService(provider_name="unsupported", model_name="model", api_key="key")
            
        assert "Unsupported provider" in str(excinfo.value)

    def test_model_prediction(self):
        """Test that the model's predict method is called correctly"""
        with patch('app.services.llm.ChatOpenAI') as mock_chat_openai:
            mock_model = MagicMock()
            mock_model.predict.return_value = "Predicted response"
            mock_chat_openai.return_value = mock_model
            
            service = LLMService(provider_name="openai", model_name="gpt-4", api_key="fake-key")
            result = service.model.predict("Test prompt")
            
            assert result == "Predicted response"
            mock_model.predict.assert_called_once_with("Test prompt")
