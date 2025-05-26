import pytest
import os
import json
from unittest.mock import patch, MagicMock, mock_open
from app.services.mcq_service import MCQService


class TestMCQService:
    """
    Unit tests for the MCQService class
    """

    @patch('app.services.mcq_service.S3Service')
    @patch('app.services.mcq_service.OCRService')
    @patch('app.services.mcq_service.os.makedirs')
    @patch('app.services.mcq_service.open', new_callable=mock_open)
    @patch('app.services.mcq_service.json.dump')
    def test_process_mcq_request_success(
        self, mock_json_dump, mock_file, mock_makedirs, mock_ocr, mock_s3
    ):
        """Test successful processing of an MCQ request"""
        # Mock the file download
        mock_s3.download_from_public_url.return_value = "/tmp/test_file.pdf"
        
        # Mock text extraction
        mock_ocr.extract_text.return_value = "Sample extracted text"
        
        # Mock LLM service for MCQ generation
        with patch('app.services.mcq_service.MCQService._generate_mcqs') as mock_generate:
            mock_mcqs = {"questions": [{"question": "Test question?"}]}
            mock_generate.return_value = mock_mcqs
            
            result = MCQService.process_mcq_request(
                project_id="test123",
                system_prompt="Generate MCQs",
                asset_files=["https://example.com/file.pdf"],
                user_prompt="Create questions about testing"
            )
            
            # Verify directory was created
            mock_makedirs.assert_called_once()
            
            # Verify file was downloaded
            mock_s3.download_from_public_url.assert_called_once()
            
            # Verify OCR was called
            mock_ocr.extract_text.assert_called_once()
            
            # Verify _generate_mcqs was called with the right parameters
            mock_generate.assert_called_once()
            args = mock_generate.call_args[0]
            assert args[0] == "Generate MCQs"  # system_prompt
            assert "Sample extracted text" in args[1]  # document_text
            assert args[2] == "Create questions about testing"  # user_prompt
            
            # Verify results were saved to file
            mock_file.assert_called()
            mock_json_dump.assert_called_once_with(mock_mcqs, mock_file(), indent=2)
            
            # Verify correct result structure
            assert result["project_id"] == "test123"
            assert result["mcqs"] == mock_mcqs
            assert result["processed_files"] == 1
            assert "result_file_path" in result

    @patch('app.services.mcq_service.S3Service')
    @patch('app.services.mcq_service.OCRService')
    @patch('app.services.mcq_service.os.makedirs')
    def test_process_mcq_request_download_error(self, mock_makedirs, mock_ocr, mock_s3):
        """Test error handling when file download fails"""
        # Mock download error
        mock_s3.download_from_public_url.side_effect = Exception("Download failed")
        
        # Also mock _generate_mcqs to avoid actual LLM calls
        with patch('app.services.mcq_service.MCQService._generate_mcqs') as mock_generate:
            # Need to raise an explicit exception here
            mock_generate.side_effect = Exception("Error processing MCQ request")
            
            with pytest.raises(Exception):
                MCQService.process_mcq_request(
                    project_id="test123",
                    system_prompt="Generate MCQs",
                    asset_files=["https://example.com/file.pdf"],
                    user_prompt="Create questions about testing"
                )
        
        # Verify OCR was not called since download failed
        mock_ocr.extract_text.assert_not_called()

    @patch('app.services.mcq_service.LLMService')
    def test_generate_mcqs_json_response(self, mock_llm_service):
        """Test _generate_mcqs with a JSON response"""
        # Set up mock for LLM service
        mock_model = MagicMock()
        mock_model.predict.return_value = '{"questions": [{"question": "Test?", "options": ["A", "B"]}]}'
        
        mock_llm_instance = MagicMock()
        mock_llm_instance.model = mock_model
        mock_llm_service.return_value = mock_llm_instance
        
        result = MCQService._generate_mcqs(
            system_prompt="Generate MCQs",
            document_text="Test document content",
            user_prompt="Generate questions"
        )
        
        # Verify the LLM service was called correctly
        mock_llm_service.assert_called_once()
        mock_model.predict.assert_called_once()
        
        # Verify the result was parsed as JSON
        assert "questions" in result
        assert isinstance(result["questions"], list)

    @patch('app.services.mcq_service.LLMService')
    def test_generate_mcqs_text_response(self, mock_llm_service):
        """Test _generate_mcqs with a non-JSON response"""
        # Set up mock for LLM service
        mock_model = MagicMock()
        mock_model.predict.return_value = "This is a text response, not JSON"
        
        mock_llm_instance = MagicMock()
        mock_llm_instance.model = mock_model
        mock_llm_service.return_value = mock_llm_instance
        
        result = MCQService._generate_mcqs(
            system_prompt="Generate MCQs",
            document_text="Test document content",
            user_prompt="Generate questions"
        )
        
        # Verify the result contains raw_response
        assert "raw_response" in result
        assert result["raw_response"] == "This is a text response, not JSON"

    @patch('app.services.mcq_service.LLMService')
    def test_generate_mcqs_truncation(self, mock_llm_service):
        """Test document truncation in _generate_mcqs for long documents"""
        # Set up mock for LLM service
        mock_model = MagicMock()
        mock_model.predict.return_value = '{"result": "success"}'
        
        mock_llm_instance = MagicMock()
        mock_llm_instance.model = mock_model
        mock_llm_service.return_value = mock_llm_instance
        
        # Create a very long document that should be truncated
        long_doc = "x" * 30000
        
        MCQService._generate_mcqs(
            system_prompt="Generate MCQs",
            document_text=long_doc,
            user_prompt="Generate questions"
        )
        
        # Check that the truncated text was passed to the LLM
        call_args = mock_model.predict.call_args[0][0]
        assert "...[truncated]" in call_args
        assert len(call_args) < 30000 + 500  # Add some buffer for prompt text

    @patch('app.services.mcq_service.LLMService')
    def test_generate_mcqs_llm_error(self, mock_llm_service):
        """Test error handling in _generate_mcqs when LLM fails"""
        # Set up mock for LLM service to raise exception
        mock_model = MagicMock()
        mock_model.predict.side_effect = Exception("LLM error")
        
        mock_llm_instance = MagicMock()
        mock_llm_instance.model = mock_model
        mock_llm_service.return_value = mock_llm_instance
        
        with pytest.raises(Exception):
            MCQService._generate_mcqs(
                system_prompt="Generate MCQs",
                document_text="Test document",
                user_prompt="Generate questions"
            )
