import pytest
import os
from unittest.mock import patch, MagicMock, mock_open
from app.services.s3_service import S3Service


class TestS3Service:
    """
    Unit tests for the S3Service class
    """

    @patch('app.services.s3_service.os.makedirs')
    @patch('app.services.s3_service.requests.get')
    @patch('builtins.open', new_callable=mock_open)
    def test_download_from_public_url(self, mock_file, mock_get, mock_makedirs):
        """Test downloading a file from a public URL"""
        # Set up mock response
        mock_response = MagicMock()
        mock_response.iter_content.return_value = [b"chunk1", b"chunk2"]
        mock_get.return_value = mock_response
        
        # Test with a URL that has a filename
        url = "https://example.com/files/document.pdf"
        local_dir = "/tmp/downloads"
        
        result = S3Service.download_from_public_url(url, local_dir)
        
        # Verify directory was created
        mock_makedirs.assert_called_once_with(local_dir, exist_ok=True)
        
        # Verify request was made
        mock_get.assert_called_once_with(url, stream=True)
        
        # Verify file was opened for writing
        expected_path = os.path.join(local_dir, "document.pdf")
        mock_file.assert_called_once_with(expected_path, 'wb')
        
        # Verify content was written
        file_handle = mock_file()
        assert file_handle.write.call_count == 2
        file_handle.write.assert_any_call(b"chunk1")
        file_handle.write.assert_any_call(b"chunk2")
        
        # Verify correct path was returned
        assert result == expected_path

    @patch('app.services.s3_service.os.makedirs')
    @patch('app.services.s3_service.requests.get')
    @patch('builtins.open', new_callable=mock_open)
    @patch('uuid.uuid4')
    def test_download_from_public_url_no_filename(self, mock_uuid, mock_file, mock_get, mock_makedirs):
        """Test downloading a file from a URL without a filename"""
        # Set up mocks
        mock_response = MagicMock()
        mock_response.iter_content.return_value = [b"chunk1"]
        mock_get.return_value = mock_response
        
        # Set up mock content type detection
        mock_head_response = MagicMock()
        mock_head_response.headers = {"content-type": "application/pdf"}
        with patch('app.services.s3_service.requests.head') as mock_head:
            mock_head.return_value = mock_head_response
            
            # Mock UUID
            mock_uuid.return_value = "abc123"
            
            # Test with a URL that has no filename
            url = "https://example.com/files/"
            local_dir = "/tmp/downloads"
            
            result = S3Service.download_from_public_url(url, local_dir)
            
            # Verify extension was guessed from content type
            mock_head.assert_called_once_with(url, allow_redirects=True)
            
            # Verify file was saved with UUID and correct extension
            expected_path = os.path.join(local_dir, "abc123.pdf")
            mock_file.assert_called_once_with(expected_path, 'wb')
            
            # Verify correct path was returned
            assert result == expected_path

    @patch('app.services.s3_service.requests.get')
    def test_download_from_public_url_error(self, mock_get):
        """Test error handling when downloading fails"""
        # Mock request to raise error
        mock_get.side_effect = Exception("Download failed")
        
        with pytest.raises(Exception):
            S3Service.download_from_public_url("https://example.com/file.pdf")

    @patch('app.services.s3_service.requests.head')
    def test_guess_extension_from_url_content_type(self, mock_head):
        """Test guessing file extension from Content-Type header"""
        # Set up content type mapping test cases
        content_types = {
            "application/pdf": ".pdf",
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "text/plain": ".txt",
            "application/msword": ".doc",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx"
        }
        
        for content_type, expected_ext in content_types.items():
            # Setup mock response with this content type
            mock_response = MagicMock()
            mock_response.headers = {"content-type": content_type}
            mock_head.return_value = mock_response
            
            # Test extension guessing
            result = S3Service._guess_extension_from_url("https://example.com/file")
            assert result == expected_ext

    def test_guess_extension_from_url_path(self):
        """Test guessing file extension from URL path"""
        # Test various file extensions in the URL path
        with patch('app.services.s3_service.requests.head') as mock_head:
            # Setup mock response with empty content type
            mock_response = MagicMock()
            mock_response.headers = {"content-type": ""}
            mock_head.return_value = mock_response
            
            extensions = {
                "https://example.com/document.pdf": ".pdf",
                "https://example.com/image.jpg": ".jpg",
                "https://example.com/image.jpeg": ".jpg",
                "https://example.com/image.png": ".png",
                "https://example.com/file.txt": ".txt",
                "https://example.com/document.doc": ".doc",
                "https://example.com/document.docx": ".docx"
            }
            
            for url, expected_ext in extensions.items():
                result = S3Service._guess_extension_from_url(url)
                assert result == expected_ext

    def test_guess_extension_from_url_fallback(self):
        """Test fallback to .bin when extension can't be determined"""
        with patch('app.services.s3_service.requests.head') as mock_head:
            # Setup mock response with unknown content type
            mock_response = MagicMock()
            mock_response.headers = {"content-type": "application/unknown"}
            mock_head.return_value = mock_response
            
            # Test with URL that has no extension
            result = S3Service._guess_extension_from_url("https://example.com/file")
            assert result == ".bin"
            
            # Test when head request fails
            mock_head.side_effect = Exception("Request failed")
            result = S3Service._guess_extension_from_url("https://example.com/file")
            assert result == ".bin"

    @patch('app.services.s3_service.boto3.client')
    def test_upload_to_s3(self, mock_boto3_client):
        """Test uploading a file to S3"""
        # Setup mock S3 client
        mock_s3_client = MagicMock()
        mock_boto3_client.return_value = mock_s3_client
        
        # Test with specified key
        result = S3Service.upload_to_s3(
            local_path="/tmp/document.pdf", 
            bucket="test-bucket",
            key="uploads/document.pdf"
        )
        
        # Verify S3 client was created with correct credentials
        mock_boto3_client.assert_called_once()
        
        # Verify upload_file was called correctly
        mock_s3_client.upload_file.assert_called_once_with(
            "/tmp/document.pdf", "test-bucket", "uploads/document.pdf"
        )
        
        # Verify correct URL was returned
        assert result == "https://test-bucket.s3.amazonaws.com/uploads/document.pdf"

    @patch('app.services.s3_service.boto3.client')
    def test_upload_to_s3_default_key(self, mock_boto3_client):
        """Test uploading a file to S3 with default key (filename)"""
        # Setup mock S3 client
        mock_s3_client = MagicMock()
        mock_boto3_client.return_value = mock_s3_client
        
        # Test without specifying key
        result = S3Service.upload_to_s3(
            local_path="/tmp/document.pdf", 
            bucket="test-bucket"
        )
        
        # Verify upload_file was called with the filename as key
        mock_s3_client.upload_file.assert_called_once_with(
            "/tmp/document.pdf", "test-bucket", "document.pdf"
        )
        
        # Verify correct URL was returned
        assert result == "https://test-bucket.s3.amazonaws.com/document.pdf"

    @patch('app.services.s3_service.boto3.client')
    def test_upload_to_s3_error(self, mock_boto3_client):
        """Test error handling when S3 upload fails"""
        # Setup mock S3 client to raise error
        mock_s3_client = MagicMock()
        mock_s3_client.upload_file.side_effect = Exception("Upload failed")
        mock_boto3_client.return_value = mock_s3_client
        
        with pytest.raises(Exception):
            S3Service.upload_to_s3(
                local_path="/tmp/document.pdf", 
                bucket="test-bucket"
            )
