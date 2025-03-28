from langchain.chat_models import init_chat_model

class LLMService:
    def __init__(self, model: str, provider: str, api_key: str):
        """
        Initialize the LLMService with a specific provider and API key.

        :param provider: The name of the LLM provider (e.g., OpenAI, Anthropic).
        :param api_key: The API key for authenticating with the LLM provider.
        """
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.model = self._initialize_model()

    def _initialize_model(self):
        """
        Initialize the LLM model using LangChain.

        :return: An instance of the LLM model.
        """
        if self.provider.lower() == "openai":
            return init_chat_model(model=self.model, model_provider=self.provider, api_key=self.api_key)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def generate_text(self, prompt: str) -> str:
        """
        Generate text using the initialized LLM model.

        :param prompt: The input prompt for the LLM.
        :return: The generated text.
        """
        return self.model(prompt)

    def __repr__(self):
        return f"LLMService(provider={self.provider}, api_key=*****)"