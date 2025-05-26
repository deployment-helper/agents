import pytest
from unittest.mock import patch, MagicMock
from app.services.video_http_client import VideoHttpClient


class TestVideoHttpClient:
    """
    Unit tests for the VideoHttpClient class
    """

    @patch('app.services.video_http_client.HttpClient')
    def test_create_video(self, mock_http_client):
        """Test creating a video with the API"""
        # Set up mock HttpClient
        mock_client = MagicMock()
        mock_http_client.return_value = mock_client
        
        # Mock API response
        mock_client.post.return_value = {"id": "video123"}
        
        # Test data
        title = "Test Video"
        desc = "This is a test video"
        thumbnail_text = "Amazing Test"
        thumbnail_visual_desc = "A beautiful sunset with text overlay"
        quotes = ["Quote 1", "Quote 2", "Quote 3"]
        project_id = "project456"
        
        # Call the method
        result = VideoHttpClient.create_video(
            title=title,
            desc=desc,
            thumbnail_text=thumbnail_text,
            thumbnail_visual_desc=thumbnail_visual_desc,
            quotes=quotes,
            project_id=project_id
        )
        
        # Verify HttpClient was created correctly
        mock_http_client.assert_called_once()
        
        # Verify post was called with the right parameters
        mock_client.post.assert_called_once()
        
        # Extract the arguments
        args, kwargs = mock_client.post.call_args
        endpoint = args[0]
        # Check if payload is in kwargs or as a positional argument
        if len(args) > 1:
            payload = args[1]  # It's the second positional argument
        else:
            # Try different parameter names API clients might use
            payload = kwargs.get("payload") or kwargs.get("json") or kwargs.get("data")
        
        # Verify endpoint contains the API key
        assert "/videos/create-with-scenes" in endpoint
        assert "key=" in endpoint
        
        # Verify payload structure
        assert payload["projectId"] == project_id
        assert payload["name"] == title
        assert payload["description"] == desc
        assert payload["visualPrompt"] == thumbnail_visual_desc
        assert payload["sceneDescriptions"] == quotes
        
        # Verify result structure
        assert "video_id" in result
        assert result["video_id"] == "video123"
        assert "video_url" in result
        assert "video123" in result["video_url"]

    @patch('app.services.video_http_client.HttpClient')
    def test_create_video_error_handling(self, mock_http_client):
        """Test error handling when creating a video fails"""
        # Set up mock HttpClient to raise exception
        mock_client = MagicMock()
        mock_client.post.side_effect = Exception("API Error")
        mock_http_client.return_value = mock_client
        
        # Test data
        title = "Test Video"
        desc = "This is a test video"
        thumbnail_text = "Amazing Test"
        thumbnail_visual_desc = "A beautiful sunset with text overlay"
        quotes = ["Quote 1", "Quote 2", "Quote 3"]
        project_id = "project456"
        
        # Verify the error is propagated
        with pytest.raises(Exception) as excinfo:
            VideoHttpClient.create_video(
                title=title,
                desc=desc,
                thumbnail_text=thumbnail_text,
                thumbnail_visual_desc=thumbnail_visual_desc,
                quotes=quotes,
                project_id=project_id
            )
            
        assert "API Error" in str(excinfo.value)
