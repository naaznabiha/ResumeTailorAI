FROM python:3.9-slim

# 1. Install system tools + Ollama
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh
ENV OLLAMA_HOST="0.0.0.0"

# 3. Copy ONLY requirements.txt first (caching optimization)
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of the app
COPY . .

# 5. Start both services
CMD ollama serve & uvicorn app:app --host 0.0.0.0 --port $PORT