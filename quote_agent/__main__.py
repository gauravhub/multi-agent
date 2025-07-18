import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import QuoteGeneratorExecutor
from observability import setup_observability, shutdown_observability

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def main():
    # Initialize observability
    langfuse_client = setup_observability()
    
    # Define agent skills - matching the original quote agent functionality
    generate_quote_skill = AgentSkill(
        id="generate_quote",
        name="Generate Quote",
        description="Generate a random inspirational quote on a given topic or theme",
        tags=["quotes", "inspiration", "motivation", "wisdom"],
        examples=[
            "Generate a quote about success",
            "Give me an inspirational quote about perseverance",
            "Create a motivational quote about teamwork"
        ],
    )

    random_quote_skill = AgentSkill(
        id="random_quote",
        name="Random Quote",
        description="Generate a completely random inspirational quote on any topic",
        tags=["quotes", "inspiration", "motivation", "random", "surprise"],
        examples=[
            "Give me a random quote",
            "Surprise me with a quote",
            "Random inspirational quote"
        ],
    )

    # Create agent card
    agent_card = AgentCard(
        name="Quote Generator Agent",
        description="Generates random inspirational quotes on various topics using OpenAI GPT models",
        url="http://localhost:8080/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[generate_quote_skill, random_quote_skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    # Create request handler with quote generator executor
    request_handler = DefaultRequestHandler(
        agent_executor=QuoteGeneratorExecutor(),
        task_store=InMemoryTaskStore(),
    )

    # Create and configure the A2A Starlette application
    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    print("🎯 Quote Generator A2A Agent")
    print("=" * 50)
    print(f"🌐 Agent will be available at: http://localhost:8080")
    print(f"📝 Agent Card: http://localhost:8080/.well-known/agent.json")
    print("🔄 A2A Endpoints: HTTP/WebSocket/SSE supported")
    if langfuse_client:
        print("📊 Observability: Enabled with Langfuse")
    else:
        print("📊 Observability: Disabled")
    print("Press Ctrl+C to stop the agent")
    print()

    try:
        # Start the server
        uvicorn.run(server.build(), host="0.0.0.0", port=8080)
    finally:
        # Cleanup observability on shutdown
        shutdown_observability()


if __name__ == "__main__":
    main() 