# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /build

# Copy requirements and install dependencies
COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && pip install --user --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* ~/.cache/pip/*

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Copy only the necessary files from the builder
COPY --from=builder /root/.local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /root/.local/bin/ /usr/local/bin/

# Copy application files
COPY . .

# Expose the application's port
EXPOSE 8000

# Define environment variables
ENV OPENAI_API_KEY="" \
    LANGSMITH_API_KEY="" \
    TAVILY_API_KEY=""

# Command to run the application
CMD ["langgraph", "dev", "--host", "0.0.0.0", "--port", "8000"]
