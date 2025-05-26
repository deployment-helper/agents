#!/bin/bash

# Script to run tests with pytest

# Install test requirements if needed
pip install -r requirements-test.txt

# Run tests with coverage
# Using PYTHONPATH to make the app module importable
PYTHONPATH=$PWD pytest tests/unit/services --cov=app.services -v
