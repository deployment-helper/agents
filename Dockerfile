# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies if needed (e.g., for specific libraries)
# RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY ./app ./app

# Expose the port the app runs on
# Expose the port specified in the PORT environment variable, default to 8000
# The EXPOSE instruction informs Docker that the container listens on the specified 
# network port at runtime. In this case, it exposes the port defined by the environment 
# variable PORT, defaulting to 8000 if PORT is not set. This does not publish the port 
# to the host automatically; it serves as metadata for the container and is used in 
# conjunction with the `-p` or `--publish` flag when running the container to map the 
# container's port to a port on the host machine.
EXPOSE ${PORT:-8000}

# Define the command to run the application
# Use 0.0.0.0 to make it accessible from outside the container
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
