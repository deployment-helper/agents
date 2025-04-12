from fastapi import FastAPI, APIRouter
import logging

from app.agents.quotes_video_agent import agent_executor
from app.graphs.quotes_video_graph import graph

from langgraph.types import Command

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


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/start")
async def start():
    """
    # TODO: Get video quotes types from the user
    Start the agent and create a video.
    """
    return agent_executor.invoke({"input": "Create a video about motivation."})


@app.get("/graph")
async def get_graph():
    """
    Get the graph of the agent.
    """
    config = {"configurable": {"thread_id": "1"}}
    print(graph.get_graph().draw_ascii())

    graph.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "I need some expert advice on how to create a video.",
                }
            ]
        },
        config=config,
    )

    human_response = (
        "We are expert and ask to google on this topic and visit nearby library"
    )

    human_command = Command(resume={"data": human_response})
    graph.invoke(human_command, config=config)

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
