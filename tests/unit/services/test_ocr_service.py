import pytest
import os
from unittest.mock import patch, MagicMock, mock_open
from app.services.ocr_service import OCRService


class TestOCRService:
    """
    Unit tests for the OCRService class
    """

    @patch('app.services.ocr_service.convert_from_path')
    @patch('app.services.ocr_service.pytesseract.image_to_string')
    def test_extract_text_from_pdf(self, mock_image_to_string, mock_convert_from_path):
        """Test extracting text from a PDF file"""
        # Set up mocks
        mock_image1 = MagicMock()
        mock_image2 = MagicMock()
        mock_convert_from_path.return_value = [mock_image1, mock_image2]
        
        # Mock OCR results for each page
        mock_image_to_string.side_effect = ["Page 1 content", "Page 2 content"]
        
        result = OCRService.extract_text_from_pdf("/path/to/test.pdf")
        
        # Verify pdf2image was called correctly
        mock_convert_from_path.assert_called_once_with("/path/to/test.pdf")
        
        # Verify pytesseract was called for each page
        assert mock_image_to_string.call_count == 2
        mock_image_to_string.assert_any_call(mock_image1, lang='eng')
        mock_image_to_string.assert_any_call(mock_image2, lang='eng')
        
        # Verify result combines both pages
        assert result == "Page 1 content\n\nPage 2 content"

    @patch('app.services.ocr_service.convert_from_path')
    @patch('app.services.ocr_service.pytesseract.image_to_string')
    def test_extract_text_from_pdf_error(self, mock_image_to_string, mock_convert_from_path):
        """Test error handling when extracting text from a PDF file fails"""
        # Mock PDF conversion error
        mock_convert_from_path.side_effect = Exception("PDF conversion failed")
        
        with pytest.raises(Exception):
            OCRService.extract_text_from_pdf("/path/to/test.pdf")
        
        # Verify pytesseract was not called
        mock_image_to_string.assert_not_called()

    @patch('app.services.ocr_service.Image.open')
    @patch('app.services.ocr_service.pytesseract.image_to_string')
    def test_extract_text_from_image(self, mock_image_to_string, mock_image_open):
        """Test extracting text from an image file"""
        # Set up mocks
        mock_image = MagicMock()
        mock_image_open.return_value = mock_image
        mock_image_to_string.return_value = "Image text content"
        
        result = OCRService.extract_text_from_image("/path/to/image.jpg")
        
        # Verify Image.open was called correctly
        mock_image_open.assert_called_once_with("/path/to/image.jpg")
        
        # Verify pytesseract was called
        mock_image_to_string.assert_called_once_with(mock_image, lang='eng')
        
        # Verify result
        assert result == "Image text content"

    @patch('app.services.ocr_service.Image.open')
    @patch('app.services.ocr_service.pytesseract.image_to_string')
    def test_extract_text_from_image_error(self, mock_image_to_string, mock_image_open):
        """Test error handling when extracting text from an image file fails"""
        # Mock image open error
        mock_image_open.side_effect = Exception("Image open failed")
        
        with pytest.raises(Exception):
            OCRService.extract_text_from_image("/path/to/image.jpg")
        
        # Verify pytesseract was not called
        mock_image_to_string.assert_not_called()

    def test_extract_text_pdf(self):
        """Test extract_text dispatches to extract_text_from_pdf for PDF files"""
        with patch('app.services.ocr_service.OCRService.extract_text_from_pdf') as mock_extract_pdf:
            mock_extract_pdf.return_value = "PDF content"
            
            result = OCRService.extract_text("/path/to/document.pdf")
            
            mock_extract_pdf.assert_called_once_with("/path/to/document.pdf")
            assert result == "PDF content"

    def test_extract_text_image(self):
        """Test extract_text dispatches to extract_text_from_image for image files"""
        with patch('app.services.ocr_service.OCRService.extract_text_from_image') as mock_extract_image:
            mock_extract_image.return_value = "Image content"
            
            # Test various image extensions
            for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']:
                result = OCRService.extract_text(f"/path/to/image{ext}")
                
                mock_extract_image.assert_called_with(f"/path/to/image{ext}")
                assert result == "Image content"
                
            # Verify the total number of calls
            assert mock_extract_image.call_count == 6

    @patch('builtins.open', new_callable=mock_open, read_data="Text file content")
    def test_extract_text_text_file(self, mock_file):
        """Test extract_text reads text files directly"""
        result = OCRService.extract_text("/path/to/document.txt")
        
        mock_file.assert_called_once_with("/path/to/document.txt", 'r', encoding='utf-8')
        assert result == "Text file content"

    def test_extract_text_unsupported_format(self):
        """Test extract_text handles unsupported file formats"""
        with patch('builtins.open') as mock_file:
            # Mock open to raise UnicodeDecodeError for binary file
            mock_file.side_effect = UnicodeDecodeError('utf-8', b'binary data', 0, 1, 'invalid start byte')
            
            # Also mock extract_text_from_image to fail
            with patch('app.services.ocr_service.OCRService.extract_text_from_image') as mock_extract_image:
                mock_extract_image.side_effect = Exception("Not an image")
                
                with pytest.raises(ValueError) as excinfo:
                    OCRService.extract_text("/path/to/document.xyz")
                    
                assert "Unsupported file format" in str(excinfo.value)
