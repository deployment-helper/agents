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


@dataclass(frozen=True)
class StorageConfig:
    temp_file_path: str = os.getenv("TEMP_FILE_PATH", os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "temp"))
    mcq_files_path: str = os.getenv("MCQ_FILES_PATH", os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "mcq"))
    aws_access_key: str = os.getenv("AWS_ACCESS_KEY", "")
    aws_secret_key: str = os.getenv("AWS_SECRET_KEY", "")


# Instantiate configuration objects
llm_config = LLMConfig()
api_config = APIConfig()
storage_config = StorageConfig()

# Ensure directories exist
os.makedirs(storage_config.temp_file_path, exist_ok=True)
os.makedirs(storage_config.mcq_files_path, exist_ok=True)
