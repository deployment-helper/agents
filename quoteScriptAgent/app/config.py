import os
from dotenv import load_dotenv
from dataclasses import dataclass

# Load environment variables
load_dotenv()


@dataclass(frozen=True)
class LLMConfig:
    provider: str = os.getenv("LLM_PROVIDER", "openai")
    model_name: str = os.getenv("LLM_MODEL", "gpt-4.1-mini")
    api_key: str = os.getenv("LLM_API_KEY", "")
    temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))


@dataclass(frozen=True)
class APIConfig:
    base_url: str = os.getenv("API_BASE_URL", "https://api.example.com")
    api_key: str = os.getenv("API_KEY", "")


# Instantiate configuration objects
llm_config = LLMConfig()
api_config = APIConfig()
