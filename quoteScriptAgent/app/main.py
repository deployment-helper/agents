from fastapi import FastAPI, APIRouter
import logging
from dotenv import load_dotenv
import os

from app.services.llm import LLMService
app = FastAPI()

# Configure logger
logger = logging.getLogger("main")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
class CustomFormatter(logging.Formatter):
    # Define color codes for log levels
    COLORS = {
        "DEBUG": "\033[94m",  # Blue
        "INFO": "\033[92m",   # Green
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",  # Red
        "CRITICAL": "\033[95m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        record.name = f"{log_color}{record.name}{self.RESET}"
        return super().format(record)

formatter = CustomFormatter("%(name)s - %(levelname)s: %(asctime)s -  %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# Load environment variables from .env file
load_dotenv()


# Load environment variables
LLM_API_KEY = os.getenv("LLM_API_KEY")

if not LLM_API_KEY:
    logger.error("API_KEY not found in environment variables.")
    raise ValueError("API_KEY not found in environment variables.")

LLM_PROVIDER = os.getenv("LLM_PROVIDER")
if not LLM_PROVIDER:
    logger.error("LLM_PROVIDER not found in environment variables.")
    raise ValueError("LLM_PROVIDER not found in environment variables.")

LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME")
if not LLM_MODEL_NAME:
    logger.error("LLM_MODEL_NAME not found in environment variables.")
    raise ValueError("LLM_MODEL_NAME not found in environment variables.")

model = LLMService(
    model=LLM_MODEL_NAME,
    provider=LLM_PROVIDER,
    api_key=LLM_API_KEY
)

@app.get('/health')
def health_check():
    return {"status": "healthy"}

@app.get('/greeting')
async def greeting():
    return model.generate_text("List your capabilities in a friendly way.")

@app.on_event("startup")
def startup_event():
    logger.info("Agent is running on http://localhost:8000")
    # Log all routes
    for route in app.routes:
        logger.info(f"Route: {route.path} | Method(s): {route.methods}")

@app.on_event("shutdown")
def shutdown_event():
    logger.info("Agent is shutting down...")
    # Clean up resources or perform shutdown tasks here
    # For example, closing database connections or stopping background tasks