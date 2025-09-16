import os
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app

# The get_fast_api_app function from the ADK automatically discovers the agent
# in the 'app' directory and wraps it in a FastAPI application.
app: FastAPI = get_fast_api_app(
    agents_dir=os.path.dirname(os.path.abspath(__file__)),
    # Using an in-memory session service for simplicity with Cloud Run.
    # For production, you might use a persistent session service like AlloyDB.
    session_service_uri="in_memory://",
    allow_origins=["*"], # Allow all origins for simplicity, adjust for production
    web=False # We don't need the ADK web UI, just the API
)
