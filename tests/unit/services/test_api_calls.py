import pytest
from unittest.mock import patch, MagicMock
from app.services.api_calls import HttpClient


class TestHttpClient:
    """
    Unit tests for the HttpClient class
    """

    def setup_method(self):
        """Setup method to run before each test"""
        self.base_url = "https://api.example.com"
        self.client = HttpClient(self.base_url)

    @patch('app.services.api_calls.requests.get')
    def test_get(self, mock_get):
        """Test GET request"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": "test"}
        mock_get.return_value = mock_response
        
        # Call the method
        result = self.client.get("endpoint")
        
        # Verify request was made correctly
        mock_get.assert_called_once_with(f"{self.base_url}/endpoint")
        assert result == {"data": "test"}

    @patch('app.services.api_calls.requests.post')
    def test_post(self, mock_post):
        """Test POST request"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 123}
        mock_post.return_value = mock_response
        
        # Test data
        data = {"name": "test"}
        
        # Call the method
        result = self.client.post("endpoint", data)
        
        # Verify request was made correctly
        mock_post.assert_called_once_with(f"{self.base_url}/endpoint", json=data)
        assert result == {"id": 123}

    @patch('app.services.api_calls.requests.put')
    def test_put(self, mock_put):
        """Test PUT request"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"updated": True}
        mock_put.return_value = mock_response
        
        # Test data
        data = {"id": 123, "name": "updated"}
        
        # Call the method
        result = self.client.put("endpoint", data)
        
        # Verify request was made correctly
        mock_put.assert_called_once_with(f"{self.base_url}/endpoint", json=data)
        assert result == {"updated": True}

    @patch('app.services.api_calls.requests.delete')
    def test_delete(self, mock_delete):
        """Test DELETE request"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"deleted": True}
        mock_delete.return_value = mock_response
        
        # Call the method
        result = self.client.delete("endpoint")
        
        # Verify request was made correctly
        mock_delete.assert_called_once_with(f"{self.base_url}/endpoint")
        assert result == {"deleted": True}

    @patch('app.services.api_calls.requests.get')
    def test_get_error_handling(self, mock_get):
        """Test error handling in GET request"""
        # Mock the request to raise an error
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        mock_get.return_value = mock_response
        
        # Verify the error is propagated
        with pytest.raises(Exception) as excinfo:
            self.client.get("endpoint")
            
        assert "HTTP Error" in str(excinfo.value)

    @patch('app.services.api_calls.requests.post')
    def test_post_error_handling(self, mock_post):
        """Test error handling in POST request"""
        # Mock the request to raise an error
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        mock_post.return_value = mock_response
        
        # Verify the error is propagated
        with pytest.raises(Exception) as excinfo:
            self.client.post("endpoint", {})
            
        assert "HTTP Error" in str(excinfo.value)
