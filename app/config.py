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
    base_url: str = os.getenv("VIDEO_API_BASE_URL", "")
    api_key: str = os.getenv("VIDEO_API_KEY", "")
    server_api_key: str = os.getenv("SERVER_API_KEY", "default_secret_key")


# Instantiate configuration objects
llm_config = LLMConfig()
api_config = APIConfig()
