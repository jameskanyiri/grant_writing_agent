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
   git clone https://github.com/ThumbPrint-Consulting/Thumbprint_v3.git
   cd Thumbprint_v3
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

## Development Guide

### Local Development Setup

1. Install development dependencies:

   ```bash
   pip install -r requirements.txt
   ```

### Project Components

- **graph.py**: Contains the main LangGraph implementation for the chatbot
- **langgraph.json**: Defines the application configuration and dependencies
- **.env**: Contains environment variables and API keys

## API Documentation

Once the server is running, access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Configuration

### Environment Variables

| Variable          | Description                              | Required |
| ----------------- | ---------------------------------------- | -------- |
| OPENAI_API_KEY    | OpenAI API key for language model access | Yes      |
| LANGCHAIN_API_KEY | LangChain API key for chain operations   | Yes      |
| REDIS_URI         | URI for Redis connection                 | Yes      |
| DATABASE_URI      | URI for PostgreSQL connection            | Yes      |

## Troubleshooting

Common issues and solutions:

1. **Connection Issues**

   - Verify Redis and PostgreSQL are running
   - Check environment variables are correctly set
   - Ensure ports are not in use

2. **API Key Issues**
   - Verify API keys are valid and properly formatted
   - Check for proper environment variable loading

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Coding Standards

- Follow PEP 8 guidelines
- Include docstrings for all functions
- Write unit tests for new features
- Update documentation as needed

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- GitHub Issues: [Create an issue](https://github.com/yourusername/grant-genie-chatbot/issues)
- Email: support@grantgenie.com
- Documentation: [Wiki](https://github.com/yourusername/grant-genie-chatbot/wiki)

## Acknowledgments

- LangGraph team for the framework
- Contributors and maintainers
- Open source community

---

## 👥 Team

- **James Kanyiri** - Lead Developer - [GitHub](https://github.com/jameskanyiri)
- **Thumbprint Consulting** - Project Owner - [Website](https://thumbprintconsulting.co.ke)

## 📞 Support

For support:

- Email: support@thumbprintconsulting.co.ke
- Join our [Slack channel](https://thumbprintconsulting.slack.com)

---
