#!/bin/bash

# Activate virtual environment if needed
source ../.venv/bin/activate

# Navigate to the directory where api_gateway.py is located
cd "../src/services/" || { echo "Directory not found"; exit 1; }

# Set PYTHONPATH to the project root
export PYTHONPATH="$(dirname "$0")/.."

# Set the FLASK_APP environment variable to the Flask app filename
export FLASK_APP=api_gateway.py

# Optionally set Flask to run in development mode (for debugging)
# export FLASK_ENV=development

# Start the Flask app
flask run --host=0.0.0.0 --port=5000  # Change port if needed
