# Grant Writing Agent (Grant Genie)

Grant Genie is a powerful AI-powered agent built with LangGraph to assist users in navigating the complex world of grant funding. It provides tools and guidance for discovering funding opportunities, drafting grant applications, and managing grant-related inquiries with the help of modern AI technologies.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Clone the Repository](#clone-the-repository)
  - [Set Up the Environment](#set-up-the-environment)
  - [Configure Environment Variables](#configure-environment-variables)
  - [Run the Application](#run-the-application)
- [Docker Deployment](#docker-deployment)
  - [Option 1: Using Docker Compose (Recommended)](#option-1-using-docker-compose-recommended)
  - [Option 2: Manual Docker Setup](#option-2-manual-docker-setup)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Features
- **Funding Discovery**: Search for relevant grants based on user criteria using AI-driven analysis.
- **Application Guidance**: Step-by-step assistance for crafting compelling grant proposals.
- **Real-time Query Handling**: Answer grant-related questions with up-to-date information.
- **Scalable Architecture**: Built with LangGraph, Redis, and PostgreSQL for robust performance.
- **Docker Support**: Easy deployment with Docker and Docker Compose.

## Prerequisites
Before setting up Grant Genie, ensure you have the following installed:
- **Python 3.12**: Required for running the application locally.
- **Docker**: For containerized deployment.
- **Docker Compose**: For orchestrating multi-container setups.
- **Redis**: For caching and session management.
- **PostgreSQL**: For persistent data storage.
- API keys for:
  - OpenAI (for AI model integration)
  - LangChain (for LangGraph functionality)
  - LangSmith (optional, for observability)

## Installation

Follow these steps to set up and run Grant Genie locally.

### Clone the Repository
Clone the repository to your local machine and navigate to the project directory:

```bash
git clone https://github.com/jameskanyiri/grant_writing_agent.git
cd grant_writing_agent
```

### Set Up the Environment
Create and activate a Python virtual environment, then install the required dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Ensure that `requirements.txt` includes all necessary dependencies, such as `langgraph`, `redis`, `psycopg2`, and any OpenAI or LangChain libraries.

### Configure Environment Variables
Create a `.env` file in the root directory to store your environment variables. Use the following template:

```bash
OPENAI_API_KEY=your_openai_api_key
LANGCHAIN_API_KEY=your_langchain_api_key
LANGSMITH_API_KEY=your_langsmith_api_key
REDIS_URI=redis://localhost:6379/0
DATABASE_URI=postgresql://username:password@localhost:5432/grant_genie
```

Replace the placeholders (`your_openai_api_key`, etc.) with your actual credentials and URIs. Ensure Redis and PostgreSQL are running and accessible at the specified URIs.

### Run the Application
Start the LangGraph application:

```bash
langgraph dev
```

This will launch the application on `http://localhost:8000` (or the configured port). You can access the Grant Genie interface via a web browser or API client.

## Docker Deployment

For containerized deployment, Grant Genie supports both Docker Compose and manual Docker setups.

### Option 1: Using Docker Compose (Recommended)
Docker Compose simplifies the process by orchestrating the application, Redis, and PostgreSQL services.

1. Ensure you have a `docker-compose.yml` file in the project root.
2. Build and start all services:

```bash
docker compose up --build
```

This command builds the Docker images and starts the containers. The application will be available at `http://localhost:8123` (or the mapped port).

### Option 2: Manual Docker Setup
For more control, you can build and run the Docker container manually.

1. Build the Docker image:

```bash
docker build -t grant_writing_agent .
```

2. Run the container with the necessary environment variables:

```bash
docker run \
    --env-file .env \
    -p 8123:8000 \
    -e REDIS_URI="redis://redis:6379/0" \
    -e DATABASE_URI="postgresql://username:password@postgres:5432/grant_genie" \
    -e LANGSMITH_API_KEY="your_langsmith_key" \
    grant_writing_agent
```

Ensure that Redis and PostgreSQL containers are running and linked appropriately (e.g., using a Docker network).