# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install dependencies
COPY pyproject.toml ./
RUN pip install uv && uv sync --no-dev

# Copy the rest of the application code
COPY main.py ./

# The port the app runs on
EXPOSE 8080

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]