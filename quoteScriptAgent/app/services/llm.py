from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.language_models import BaseChatModel
class LLMService:
    def __init__(self, provider_name: str,  model_name: str, api_key: str):
        """
        Initialize the LLMService with a specific provider and API key.

        :param provider: The name of the LLM provider (e.g., OpenAI, Anthropic).
        :param api_key: The API key for authenticating with the LLM provider.
        """
        
        self.provider_name = provider_name
        self.api_key = api_key
        self.model_name = model_name
        self.model = self._initialize_model()

    def _initialize_model(self) -> BaseChatModel:
        """
        Initialize the LLM model using LangChain.

        :return: An instance of the LLM model.
        """
        if self.provider_name.lower() == "openai":
            return ChatOpenAI(
                model_name=self.model_name,
                openai_api_key=self.api_key)
        else:
            raise ValueError(f"Unsupported provider: {self.provider_name}, {self}")