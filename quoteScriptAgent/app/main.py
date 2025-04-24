from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from app.agents.quotes_video_agent import agent_executor
from app.graphs.quotes_video_graph import graph
from app.config import api_config  # Import api_config

from langgraph.types import Command
from pydantic import BaseModel

app = FastAPI()

# Configure logger
logger = logging.getLogger("main")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()


class CustomFormatter(logging.Formatter):
    # Define color codes for log levels
    COLORS = {
        "DEBUG": "\033[94m",  # Blue
        "INFO": "\033[92m",  # Green
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

# Security scheme
security = HTTPBearer()

# Dependency to verify API key
async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify the provided API key."""
    if not credentials or credentials.scheme != "Bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if credentials.credentials != api_config.server_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials

@app.get("/health")
def health_check():
    return {"status": "healthy"}


class GraphRequest(BaseModel):
    topic: str

@app.post("/graph", dependencies=[Depends(verify_api_key)]) # Add dependency here
async def get_graph(request: GraphRequest):
    """
    Get the graph of the agent. Requires API Key authentication.
    """
    config = {"configurable": {"thread_id": "1"}}

    graph.invoke(
        {
            "topic": request.topic,
        },
        config=config,
    )
    return graph.get_state(config=config)


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
