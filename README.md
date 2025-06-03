# Grant Writing Agent

Grant Genie is a LangGraph-powered agent designed to assist users with grant-related inquiries. It leverages modern AI tooling to streamline funding discovery and application guidance.

## Prerequisites

- Python 3.12
- Docker
- Docker Compose
- Redis
- PostgreSQL


## Quick Start

1. **Clone the repository:**

   ```bash
   git clone https://github.com/jameskanyiri/grant_writing_agent.git
   cd grant_writing_agent
   ```

2. **Set up environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   Create a `.env` file in the root directory:

   ```bash
   OPENAI_API_KEY=your_openai_api_key
   LANGCHAIN_API_KEY=your_langchain_api_key
   REDIS_URI=your_redis_uri
   DATABASE_URI=your_database_uri
   ```

4. **Run the application:**
   ```bash
   langgraph dev
   ```

## Docker Deployment

### Option 1: Using Docker Compose (Recommended)

1. Build and run all services:
   ```bash
   docker compose up --build
   ```

### Option 2: Manual Docker Setup

1. Build the Docker image:

   ```bash
   langgraph build -t grant-genie-image
   ```

2. Run the container:
   ```bash
   docker run \
       --env-file .env \
       -p 8123:8000 \
       -e REDIS_URI="your_redis_uri" \
       -e DATABASE_URI="your_database_uri" \
       -e LANGSMITH_API_KEY="your_langsmith_key" \
       grant-genie-image
   ```
