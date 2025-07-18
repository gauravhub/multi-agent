import uuid
import asyncio
import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    AgentCard,
    Message,
    MessageSendParams,
    Part,
    Role,
    SendMessageRequest,
    TextPart,
)

PUBLIC_AGENT_CARD_PATH = "/.well-known/agent.json"
BASE_URL = "http://localhost:8080"


async def test_quote_generation():
    """Test the quote generation functionality of the agent."""
    async with httpx.AsyncClient(timeout=30.0) as httpx_client:
        # Initialize A2ACardResolver
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=BASE_URL,
        )

        final_agent_card_to_use: AgentCard | None = None

        try:
            print(f"🔍 Fetching agent card from: {BASE_URL}{PUBLIC_AGENT_CARD_PATH}")
            _public_card = await resolver.get_agent_card()
            print("✅ Fetched agent card successfully")
            print(f"📝 Agent: {_public_card.name}")
            print(f"📋 Description: {_public_card.description}")
            print(f"🛠️  Skills: {len(_public_card.skills)} available")
            for skill in _public_card.skills:
                print(f"   - {skill.name}: {skill.description}")
            print()

            final_agent_card_to_use = _public_card

        except Exception as e:
            print(f"❌ Error fetching agent card: {e}")
            raise RuntimeError("Failed to fetch agent card")

        # Initialize A2A client
        client = A2AClient(
            httpx_client=httpx_client, 
            agent_card=final_agent_card_to_use
        )
        print("✅ A2A Client initialized")
        print()

        # Test cases for quote generation
        test_messages = [
            "Generate a quote about success",
            "Give me an inspirational quote about courage",
            "Create a quote about teamwork",
            "Give me a random quote",
            "Surprise me with a quote",
            "Generate a motivational quote"
        ]

        print("🧪 Starting Quote Generation Tests")
        print("=" * 50)

        for i, test_message in enumerate(test_messages, 1):
            try:
                print(f"Test {i}: '{test_message}'")
                
                # Create message payload
                message_payload = Message(
                    role=Role.user,
                    messageId=str(uuid.uuid4()),
                    parts=[Part(root=TextPart(text=test_message))],
                )
                
                # Create request
                request = SendMessageRequest(
                    id=str(uuid.uuid4()),
                    params=MessageSendParams(
                        message=message_payload,
                    ),
                )
                
                print(f"📤 Sending: '{test_message}'")
                
                # Send message and get response
                response = await client.send_message(request)
                
                # Extract and display the quote
                if hasattr(response, 'root') and hasattr(response.root, 'result'):
                    message_result = response.root.result
                    if hasattr(message_result, 'parts') and message_result.parts:
                        quote_text = message_result.parts[0].root.text
                        print(f"📥 Response: {quote_text}")
                        print("✅ Test passed")
                    else:
                        print("❌ No quote text found in response")
                        print(f"Debug - message_result: {message_result}")
                else:
                    print("❌ Unexpected response format")
                    print(f"Response: {response}")
                
                print("-" * 50)
                
                # Small delay between requests
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"❌ Test {i} failed: {e}")
                print("-" * 50)

        print("🎯 Quote Generation Tests Completed!")


async def interactive_mode():
    """Interactive mode for testing quote generation."""
    async with httpx.AsyncClient(timeout=30.0) as httpx_client:
        try:
            # Initialize resolver and client
            resolver = A2ACardResolver(httpx_client=httpx_client, base_url=BASE_URL)
            agent_card = await resolver.get_agent_card()
            client = A2AClient(httpx_client=httpx_client, agent_card=agent_card)
            
            print("🎮 Interactive Quote Generator Test Mode")
            print("Type 'quit' to exit")
            print("-" * 40)
            
            while True:
                try:
                    user_input = input("\nEnter your quote request: ").strip()
                    
                    if user_input.lower() in ['quit', 'exit', 'q']:
                        print("👋 Goodbye!")
                        break
                    
                    if not user_input:
                        print("Please enter a quote request.")
                        continue
                    
                    # Create and send message
                    message_payload = Message(
                        role=Role.user,
                        messageId=str(uuid.uuid4()),
                        parts=[Part(root=TextPart(text=user_input))],
                    )
                    
                    request = SendMessageRequest(
                        id=str(uuid.uuid4()),
                        params=MessageSendParams(message=message_payload),
                    )
                    
                    print(f"🔄 Generating quote...")
                    response = await client.send_message(request)
                    
                    # Extract and display the quote
                    if hasattr(response, 'root') and hasattr(response.root, 'result'):
                        message_result = response.root.result
                        if hasattr(message_result, 'parts') and message_result.parts:
                            quote_text = message_result.parts[0].root.text
                            print(f"✨ {quote_text}")
                        else:
                            print("❌ No quote received")
                    else:
                        print("❌ Unexpected response format")
                        
                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
                    
        except Exception as e:
            print(f"❌ Failed to initialize client: {e}")


async def main():
    """Main test function."""
    print("🎯 Quote Generator A2A Agent - Test Client")
    print("=" * 50)
    print()
    
    try:
        # Check if agent is running
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/.well-known/agent.json", timeout=5)
            if response.status_code == 200:
                print("✅ Agent is running and accessible")
            else:
                print(f"⚠️ Agent responded with status {response.status_code}")
    except Exception as e:
        print(f"❌ Agent is not running or not accessible: {e}")
        print("Please start the agent first with: uv run .")
        return
    
    print()
    print("Choose test mode:")
    print("1. Automated tests")
    print("2. Interactive mode")
    
    try:
        choice = input("Enter your choice (1 or 2): ").strip()
        
        if choice == "1":
            await test_quote_generation()
        elif choice == "2":
            await interactive_mode()
        else:
            print("Invalid choice. Running automated tests...")
            await test_quote_generation()
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")


if __name__ == "__main__":
    asyncio.run(main()) 