from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import logging

from langgraph.types import Command
from pydantic import BaseModel
from typing import Literal

from app.agents.quotes_video_agent import agent_executor
from app.graphs.quotes_video_graph import graph
from app.config import api_config  # Import api_config
from app.services.topics import get_random_topic
from app.services.mcq_service import MCQService



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

# Configure root logger to ensure all module loggers have handlers
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_handler = logging.StreamHandler()
root_handler.setFormatter(formatter)
root_logger.addHandler(root_handler)

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
    topic: str = None  # Make topic optional
    project_id: str  # Add project_id field

class MCQRequest(BaseModel):
    project_id: str
    system_prompt: str
    asset_files: list[str] = [] 
    user_prompt: str

class ConversationRequest(BaseModel):
    user_input: str
    project_id: str
    video_type: Literal['message','mcq']
    context: dict = None

@app.post("/graph", dependencies=[Depends(verify_api_key)]) # Add dependency here
async def get_graph(request: GraphRequest):
    """
    Get the graph of the agent. Requires API Key authentication.
    """
    config = {"configurable": {"thread_id": "1"}}

    # Pass project_id along with topic
    graph.invoke(
        {
            # Use the provided topic if available, otherwise pick a random one
            "topic": request.topic if request.topic else get_random_topic(),
            "project_id": request.project_id,
        },
        config=config,
    )
    return graph.get_state(config=config)

@app.post("/mcq", dependencies=[Depends(verify_api_key)]) # Add dependency here
async def create_mcq(req: MCQRequest):
    """
    Create MCQs from provided files and prompts. 
    This endpoint processes asset files (PDFs) using OCR and generates MCQs based on their content.
    
    Args:
        req (MCQRequest): Request containing project_id, system_prompt, asset_files, and user_prompt
    
    Returns:
        dict: The generated MCQs and related metadata
    """
    try:
        logger.info(f"MCQ generation requested for project: {req.project_id}")
        logger.info(f"Processing {len(req.asset_files)} asset files")
        
        # Process the request using static method
        result = MCQService.process_mcq_request(
            project_id=req.project_id,
            system_prompt=req.system_prompt,
            asset_files=req.asset_files,
            user_prompt=req.user_prompt
        )
        
        logger.info(f"MCQ generation complete for project: {req.project_id}")
        return result
    
    except Exception as e:
        logger.error(f"Error in MCQ generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"MCQ generation failed: {str(e)}"
        )

@app.post("/conversation", dependencies=[Depends(verify_api_key)])
async def conversation(req:ConversationRequest):
    """
    Handle conversation requests with the agent.
    This endpoint processes user input and returns the agent's response.
    
    Args:
        req (dict): Request containing user input and other parameters
    
    Returns:
        dict: The agent's response
    """
    try:
        logger.info("Processing conversation request")            
        return req.user_input
    
    except Exception as e:
        logger.error(f"Error in conversation processing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Conversation processing failed: {str(e)}"
        )

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
