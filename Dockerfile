# Use a lightweight Python base image
FROM python:3.9-slim

# Install system dependencies (required for Ollama)
RUN apt-get update && apt-get install -y curl

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Set Ollama to serve in the background
ENV OLLAMA_HOST="0.0.0.0"

# Copy your FastAPI app files
WORKDIR /app
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Start both Ollama and FastAPI
CMD ollama serve & uvicorn app:app --host 0.0.0.0 --port $PORT