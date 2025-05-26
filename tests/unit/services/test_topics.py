import pytest
from unittest.mock import patch
from app.services.topics import TOPICS, get_random_topic


class TestTopics:
    """
    Unit tests for the topics module functionality
    """

    def test_topics_list(self):
        """Test that the TOPICS list is properly defined"""
        # Verify the list is not empty
        assert len(TOPICS) > 0
        
        # Verify all topics are strings
        assert all(isinstance(topic, str) for topic in TOPICS)
        
        # Verify some specific topics are in the list
        assert "Love Quotes" in TOPICS
        assert "Inspirational Quotes" in TOPICS
        assert "Motivational Quotes" in TOPICS

    @patch('app.services.topics.random.choice')
    def test_get_random_topic(self, mock_choice):
        """Test the get_random_topic function"""
        # Set up mock to return a specific topic
        mock_choice.return_value = "Test Topic"
        
        # Call the function
        result = get_random_topic()
        
        # Verify random.choice was called with TOPICS list
        mock_choice.assert_called_once_with(TOPICS)
        
        # Verify the result matches the mock
        assert result == "Test Topic"

    def test_get_random_topic_returns_valid_topic(self):
        """Test that get_random_topic returns an actual topic from the list"""
        # Call the function
        result = get_random_topic()
        
        # Verify the result is in the TOPICS list
        assert result in TOPICS
