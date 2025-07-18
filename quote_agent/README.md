# Quote Generator A2A Agent 🎯

A simple A2A (Agent-to-Agent) agent that generates inspirational quotes using OpenAI GPT models, built following the [bhancockio/agent2agent](https://github.com/bhancockio/agent2agent) `a2a_simple` pattern.

This application demonstrates the A2A SDK by creating a quote generation agent that can:
- Generate topic-specific inspirational quotes
- Create random motivational quotes  
- Respond via HTTP, WebSocket, and Server-Sent Events

## Features ✨

- **A2A Protocol Compliant**: Built with `a2a-sdk` using Starlette/ASGI
- **OpenAI GPT Integration**: Uses OpenAI's GPT models for quote generation
- **Two Skills**:
  - **Generate Quote**: Create quotes on specific topics
  - **Random Quote**: Generate completely random inspirational quotes
- **Multiple Transport Support**: HTTP, WebSocket, SSE automatically supported
- **Environment-based Configuration**: Easy configuration via environment variables
- **Comprehensive Testing**: Automated and interactive test modes
- **Full Observability**: Integrated with Langfuse and OpenInference for LLM monitoring
- **OpenTelemetry Support**: Distributed tracing and metrics collection

## Project Structure 📁

```
quote_agent/
├── __init__.py           # Package initialization (empty)
├── __main__.py           # Main application entry point
├── agent_executor.py     # Quote generation logic and executor
├── observability.py      # Langfuse and OpenInference observability setup
├── test_client.py        # A2A client for testing
├── pyproject.toml        # Project configuration and dependencies
├── README.md             # This documentation
└── env.example           # Environment variables template
```

## Setup and Deployment 🚀

### Prerequisites

Before running the application, ensure you have:

1. **uv**: The Python package management tool used in this project. Follow the installation guide: [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)
2. **Python 3.10+**: Python 3.10 or higher is required to run a2a-sdk
3. **OpenAI API Key**: You'll need an OpenAI API key for GPT access

### 1. Install Dependencies

This will create a virtual environment in the `.venv` directory and install the required packages:

```bash
cd quote_agent_simple
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

### 2. Configuration

Create a `.env` file with your OpenAI API key:

```bash
# Copy the example and edit
cp .env.example .env

# Edit .env and add your OpenAI API key:
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
LOG_LEVEL=INFO
```

### 3. Run the Agent

Open a terminal and run the agent:

```bash
uv run .
```

The agent will be running on `http://localhost:8080` and you'll see:

```
🎯 Quote Generator A2A Agent
==================================================
🌐 Agent will be available at: http://localhost:8080
📝 Agent Card: http://localhost:8080/.well-known/agent.json
🔄 A2A Endpoints: HTTP/WebSocket/SSE supported
📊 Observability: Enabled with Langfuse (if configured)
Press Ctrl+C to stop the agent
```

### 4. Test the Agent

Open a new terminal and run the test client:

```bash
uv run --active test_client.py
```

You will see options for:
- **Automated tests**: Run predefined test cases
- **Interactive mode**: Chat with the agent in real-time

## Usage Examples 💡

### Agent Skills

The agent provides two main skills:

#### 1. Generate Quote
Generate an inspirational quote on a specific topic:
- "Generate a quote about success"
- "Give me an inspirational quote about perseverance" 
- "Create a motivational quote about teamwork"

#### 2. Random Quote
Generate a completely random inspirational quote:
- "Give me a random quote"
- "Surprise me with a quote"
- "Random inspirational quote"

## Observability 📊

The Quote Generator Agent includes comprehensive observability features using Langfuse and OpenInference libraries to monitor and analyze LLM performance.

### Features

- **🔍 Request Tracing**: Track complete request lifecycle from user input to response
- **🤖 LLM Monitoring**: Monitor OpenAI API calls with detailed metrics
- **📈 Performance Analytics**: Track token usage, latency, and success rates
- **🚨 Error Tracking**: Capture and analyze failures with full context
- **📊 Cost Monitoring**: Track OpenAI API costs and usage patterns

### Setup Langfuse

1. **Create Langfuse Account**: 
   - Sign up at [https://cloud.langfuse.com](https://cloud.langfuse.com)
   - Or deploy self-hosted Langfuse instance

2. **Get API Keys**:
   - Navigate to Settings → API Keys
   - Create new API key pair (Public + Secret)

3. **Configure Environment Variables**:
   ```bash
   # Copy the example file
   cp env.example .env
   
   # Edit .env with your Langfuse credentials
   LANGFUSE_SECRET_KEY=sk-lf-...
   LANGFUSE_PUBLIC_KEY=pk-lf-...
   LANGFUSE_HOST=https://cloud.langfuse.com
   LANGFUSE_ENABLED=true
   ```

### Observability Data

The agent automatically tracks:

#### 📋 **Request Traces**
- User message input
- Request routing (topic vs random)
- Final quote output
- Processing time and status

#### 🤖 **LLM Generations**
- Model used (e.g., gpt-3.5-turbo)
- Input prompts and system messages
- Generated responses
- Token usage (input/output/total)
- API latency and costs

#### 📊 **Metadata**
- Agent version and configuration
- Request types and topics
- Success/failure rates
- Performance metrics

### Viewing Observability Data

1. **Langfuse Dashboard**: Visit your Langfuse instance to view:
   - Real-time traces and generations
   - Performance analytics and charts
   - Cost analysis and token usage
   - Error rates and debugging info

2. **OpenTelemetry Integration**: 
   - Traces are also exported via OpenTelemetry
   - Compatible with other observability platforms
   - Distributed tracing support

### Disabling Observability

Set `LANGFUSE_ENABLED=false` in your `.env` file to disable observability features.

### A2A Protocol Endpoints

The agent automatically exposes multiple endpoints:

- **Agent Card**: `GET /.well-known/agent.json`
- **HTTP Messages**: `POST /message/send` 
- **WebSocket**: `WS /ws`
- **Server-Sent Events**: `GET /events`

### Direct HTTP Testing

```bash
# Get agent card
curl http://localhost:8080/.well-known/agent.json

# Send a message request
curl -X POST http://localhost:8080/message/send \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "test-123",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "messageId": "msg-123",
        "parts": [
          {
            "root": {
              "text": "Generate a quote about courage"
            }
          }
        ]
      }
    }
  }'
```

## Architecture 🏗️

This agent follows the `a2a_simple` pattern from [bhancockio/agent2agent](https://github.com/bhancockio/agent2agent):

### Components

1. **`__main__.py`**: 
   - Creates `AgentCard` with skills metadata
   - Configures `A2AStarletteApplication` 
   - Starts Uvicorn server

2. **`agent_executor.py`**:
   - `QuoteGenerator`: Pydantic model with OpenAI integration
   - `QuoteGeneratorExecutor`: Implements `AgentExecutor` for A2A protocol
   - Message processing and quote generation logic

3. **`test_client.py`**:
   - A2A client for testing the agent
   - Automated test suite and interactive mode

### Key Differences from python_a2a

- Uses `a2a-sdk` instead of `python_a2a` 
- Built on Starlette/ASGI instead of higher-level abstractions
- Follows Google's official A2A SDK patterns
- Automatic support for multiple transport protocols (HTTP/WS/SSE)

## Configuration Options ⚙️

Environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-3.5-turbo` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `LANGFUSE_SECRET_KEY` | Langfuse secret key | - |
| `LANGFUSE_PUBLIC_KEY` | Langfuse public key | - |
| `LANGFUSE_HOST` | Langfuse host URL | `https://cloud.langfuse.com` |
| `LANGFUSE_ENABLED` | Enable/disable observability | `false` |
| `OTEL_SERVICE_NAME` | OpenTelemetry service name | `quote-agent` |
| `OTEL_SERVICE_VERSION` | OpenTelemetry service version | `1.0.0` |

## Development 🔧

### Code Structure

- **Agent Logic**: All quote generation in `QuoteGenerator` class
- **A2A Integration**: `QuoteGeneratorExecutor` handles A2A protocol
- **Configuration**: Environment-based with sensible defaults
- **Testing**: Comprehensive test client with multiple modes

### Extending the Agent

To add new quote generation capabilities:

1. Add methods to `QuoteGenerator` class
2. Update message routing in `QuoteGeneratorExecutor._extract_topic()`
3. Add new `AgentSkill` definitions in `__main__.py`

## Integration with Other Agents 🤝

This agent can be easily integrated into A2A agent networks:

```python
from a2a.client import A2AClient, A2ACardResolver

# Connect to the quote agent
async with httpx.AsyncClient() as client:
    resolver = A2ACardResolver(client, "http://localhost:8080")
    agent_card = await resolver.get_agent_card()
    quote_client = A2AClient(client, agent_card)
    
    # Use in workflows
    response = await quote_client.send_message(request)
```

## Troubleshooting 🔍

### Common Issues

1. **Agent won't start**: 
   - Check if OpenAI API key is set in `.env`
   - Verify port 8080 is available
   - Check dependencies are installed with `uv pip list`

2. **No quotes generated**:
   - Verify OpenAI API key is valid
   - Check internet connection
   - Review logs for error messages

3. **Test client fails**:
   - Ensure agent is running before tests
   - Check the base URL in `test_client.py`
   - Verify A2A client can connect

### Debug Mode

Set `LOG_LEVEL=DEBUG` in your `.env` file for detailed logging:

```bash
LOG_LEVEL=DEBUG
```

## References 📚

- [bhancockio/agent2agent](https://github.com/bhancockio/agent2agent) - Original repository and patterns
- [A2A SDK Documentation](https://github.com/google/a2a-python)  
- [A2A Protocol Specification](https://codelabs.developers.google.com/intro-a2a-purchasing-concierge#1)

## License 📄

This project follows the same patterns as the original bhancockio/agent2agent repository. 