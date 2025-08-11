# Use an official Python runtime as a parent image
# Using a slim version for a smaller image size
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
# This allows Docker to cache dependencies if requirements.txt doesn't change
COPY requirements.txt ./

# Install dependencies
# Upgrade pip first, then install packages, disabling cache to keep image smaller
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
# This includes src/, static/, config.json, etc.
COPY . .

# Expose the port the application runs on
# FastAPI/Uvicorn typically runs on 8000
EXPOSE 8000

# Define the command to run the application
# We use Gunicorn with Uvicorn workers for production-readiness.
# -w: Number of worker processes. Adjust based on your CPU cores and desired concurrency. 4 is a common starting point.
# -k uvicorn.workers.UvicornWorker: Specifies to use Uvicorn's async worker class.
# src.api:app: Points to the FastAPI application instance ('app') within the 'src.api' module.
# --bind 0.0.0.0:8000: Binds the server to all available network interfaces on port 8000, making it accessible from outside the container.
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "src.api:app", "--bind", "0.0.0.0:8000"]