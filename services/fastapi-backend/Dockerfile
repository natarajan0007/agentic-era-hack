# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install uv
RUN pip install uv

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN uv pip install -r requirements.txt --no-cache-dir

# Copy the rest of the application code
COPY . .

# The port the app runs on
EXPOSE 8080

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]