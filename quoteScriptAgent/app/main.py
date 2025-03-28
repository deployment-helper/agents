from fastapi import FastAPI
import logging

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
        return super().format(record)

formatter = CustomFormatter("%(levelname)s: %(asctime)s - %(name)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Quote Script Agent!"}


@app.on_event("startup")
def startup_event():
    logger.info("Agent is running on http://localhost:8000")
    # Initialize any resources or perform startup tasks here

@app.on_event("shutdown")
def shutdown_event():
    logger.info("Agent is shutting down...")
    # Clean up resources or perform shutdown tasks here
    # For example, closing database connections or stopping background tasks