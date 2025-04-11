from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
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

    def _initialize_model(self):
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

    def generate_video_metadata(self) -> str:
        """
        Generate video metadata including YouTube video titles, thumbnail text, 
        and quotes using the initialized LLM model.
        This method performs the following steps:
        1. Generates 10 sets of YouTube video titles and thumbnail text for a given topic.
        2. Filters and selects the best set of title and thumbnail text from the generated options.
        3. Generates 50 quotes based on the selected title and thumbnail text.
        :return: A string containing 50 quotes generated from the best title and thumbnail text.
        """
        # TODO: Read those prompts from somewhere
        sysMessage = SystemMessage(content="You are a helpful video content generation assistant. "
                                          "You will help me generate video metadata including YouTube video titles, thumbnail text, and quotes.")
        # Generate 10 sets of YouTube video titles and thumbnail text
        # for the topic 'How to be motivated in life'
        # and filter out the best one
        prompt1 = HumanMessage(content="Generate 10 sets of YouTube video titles and thumbnail text for the following topic: 'How to be motivated in life'.")
        messages = [sysMessage, prompt1]
        response = self.model(messages)

        # Use the response as input for the next prompt
        new_prompt = HumanMessage(content="From the 10 sets you generated, filter out and provide the best 1 set of title and thumbnail text.")
        messages.append(response)
        messages.append(new_prompt)

        # Generate the final response
        response2 = self.model(messages)
        
        # Generate 50 quotes from the best title 
        # and thumbnail text
        prompt2 = HumanMessage(content="Generate 50 quotes from the best title and thumbnail text.")
        messages.append(response2)
        messages.append(prompt2)
        response3 = self.model(messages)
        # TODO: this response should be structured and a list
        # TODO: we should respond with complete metadata like title, thumbnail text, and quotes
        return response3.content
    
        
    def __repr__(self):
        return f"LLMService(provider={self.provider_name}, api_key=*****)"