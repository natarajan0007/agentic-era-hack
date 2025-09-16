import os
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app

# The get_fast_api_app function from the ADK automatically discovers the agent
# in the current directory and wraps it in a FastAPI application.
app: FastAPI = get_fast_api_app(
    agents_dir=os.path.dirname(os.path.abspath(__file__)),
    session_service_uri="in_memory://",
    allow_origins=["*"], 
    web=False
)
