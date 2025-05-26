import pytest
from app.services.prompts import Prompts
from langchain_core.prompts import ChatPromptTemplate


class TestPrompts:
    """
    Unit tests for the Prompts class
    """

    def test_get_prompt(self):
        """Test retrieving predefined prompts"""
        # Test existing prompts
        assert Prompts.get_prompt("greeting") == "Hello! How can I assist you today?"
        assert Prompts.get_prompt("farewell") == "Goodbye! Have a great day!"
        assert Prompts.get_prompt("help") == "Here are some commands you can use: ..."
        
        # Test non-existent prompt
        assert Prompts.get_prompt("nonexistent") == "Prompt not found."

    def test_create_titles_thumbnails_prompt(self):
        """Test creating titles and thumbnails prompt"""
        prompt = Prompts.create_titles_thumbnails_prompt()
        
        # Verify it's the right type
        assert isinstance(prompt, ChatPromptTemplate)
        
        # Verify the prompt structure
        messages = prompt.messages
        assert len(messages) == 2
        
        # Check system message
        system_msg = messages[0]
        assert system_msg.prompt.template.startswith("you are expert youtube content creator")
        
        # Check user message
        user_msg = messages[1]
        assert "create list of titles and a list of thumbnail texts" in user_msg.prompt.template
        assert "{topic}" in user_msg.prompt.template

    def test_find_best_title_thumbnail_prompt(self):
        """Test creating prompt to find best title and thumbnail"""
        prompt = Prompts.find_best_title_thumbnail_prompt()
        
        # Verify it's the right type
        assert isinstance(prompt, ChatPromptTemplate)
        
        # Verify the prompt structure
        messages = prompt.messages
        assert len(messages) == 2
        
        # Check system message
        system_msg = messages[0]
        assert "expert youtube content creator" in system_msg.prompt.template
        
        # Check user message
        user_msg = messages[1]
        assert "select best title and thumbnail" in user_msg.prompt.template
        assert "{titles}" in user_msg.prompt.template
        assert "{thumbnail_text_list}" in user_msg.prompt.template

    def test_create_quotes_prompt(self):
        """Test creating quotes generation prompt"""
        prompt = Prompts.create_quotes_prompt()
        
        # Verify it's the right type
        assert isinstance(prompt, ChatPromptTemplate)
        
        # Verify the prompt structure
        messages = prompt.messages
        assert len(messages) == 2
        
        # Check system message
        system_msg = messages[0]
        assert "expert youtube content creator" in system_msg.prompt.template
        
        # Check user message
        user_msg = messages[1]
        assert "create a list of 40-50 quotes" in user_msg.prompt.template
        assert "{best_title}" in user_msg.prompt.template
        assert "{best_thumbnail_text}" in user_msg.prompt.template

    def test_create_thumbnail_visual_desc_prompt(self):
        """Test creating thumbnail visual description prompt"""
        prompt = Prompts.create_thumbnail_visual_desc_prompt()
        
        # Verify it's the right type
        assert isinstance(prompt, ChatPromptTemplate)
        
        # Verify the prompt structure
        messages = prompt.messages
        assert len(messages) == 2
        
        # Check system message
        system_msg = messages[0]
        assert "expert midjourney prompt creator" in system_msg.prompt.template
        
        # Check user message  
        user_msg = messages[1]
        assert "create a image description for youtube thumbnail" in user_msg.prompt.template
        assert "{best_title}" in user_msg.prompt.template
        assert "{best_thumbnail_text}" in user_msg.prompt.template

    def test_create_description_prompt(self):
        """Test creating video description prompt"""
        prompt = Prompts.create_description_prompt()
        
        # Verify it's the right type
        assert isinstance(prompt, ChatPromptTemplate)
        
        # Verify the prompt structure
        messages = prompt.messages
        assert len(messages) == 2
        
        # Check system message
        system_msg = messages[0]
        assert "expert youtube content creator" in system_msg.prompt.template
        assert "{topic}" in system_msg.prompt.template
        
        # Check user message
        user_msg = messages[1]
        assert "create a description for the youtube video" in user_msg.prompt.template
        assert "{best_title}" in user_msg.prompt.template 
        assert "{best_thumbnail_text}" in user_msg.prompt.template
