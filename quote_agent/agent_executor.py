import os
import logging
from typing import Optional
from openai import OpenAI
from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from pydantic import BaseModel, ConfigDict

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QuoteGenerator(BaseModel):
    """Quote generator that creates inspirational quotes using OpenAI GPT models."""
    
    # Private attributes are allowed in Pydantic models
    _client: Optional[OpenAI] = None
    
    def __init__(self, **data):
        super().__init__(**data)
        # Initialize the OpenAI client as a private attribute
        self._client = self._initialize_openai_client()
    
    def _initialize_openai_client(self) -> Optional[OpenAI]:
        """Initialize OpenAI client with API key from environment."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("❌ OPENAI_API_KEY not found in environment variables")
            return None
        
        try:
            client = OpenAI(api_key=api_key)
            logger.info("✅ OpenAI client initialized successfully")
            return client
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenAI client: {e}")
            return None
    
    async def generate_quote(self, topic: str = "general inspiration") -> str:
        """Generate a quote on the specified topic."""
        if not self._client:
            return "Sorry, the quote generation service is currently unavailable. Please check the OpenAI API key configuration."
        
        try:
            # Create a prompt for generating quotes
            prompt = f"""Generate a single, original inspirational quote about {topic}. 
            The quote should be:
            - Meaningful and thought-provoking
            - Concise (1-2 sentences maximum)
            - Suitable for motivation or reflection
            - Original (not a famous existing quote)
            
            Format: Just return the quote with proper attribution like "Quote" - Anonymous
            
            Topic: {topic}"""
            
            logger.info(f"🔵 Generating quote for topic: '{topic}'")
            
            response = self._client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=[
                    {"role": "system", "content": "You are a wise quote generator that creates original, inspirational quotes."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.8
            )
            
            quote = response.choices[0].message.content.strip()
            logger.info(f"🔴 Generated quote: {quote[:50]}...")
            logger.debug(f"🔴 Token usage: {response.usage.total_tokens}")
            
            return quote
            
        except Exception as e:
            logger.error(f"Error generating quote for topic '{topic}': {e}")
            return f"Sorry, I couldn't generate a quote about {topic} at the moment. Please try again later."
    
    async def random_quote(self) -> str:
        """Generate a random inspirational quote."""
        if not self._client:
            return "Sorry, the quote generation service is currently unavailable. Please check the OpenAI API key configuration."
        
        try:
            # Create a prompt for generating random quotes
            prompt = """Generate a single, original inspirational quote on any topic you choose. 
            The quote should be:
            - Meaningful and thought-provoking
            - Concise (1-2 sentences maximum)
            - Suitable for motivation or reflection
            - Original (not a famous existing quote)
            - On a randomly chosen topic (success, courage, love, growth, wisdom, etc.)
            
            Format: Just return the quote with proper attribution like "Quote" - Anonymous
            
            Choose any inspiring topic you like!"""
            
            logger.info("🔵 Generating random quote")
            
            response = self._client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=[
                    {"role": "system", "content": "You are a wise quote generator that creates original, inspirational quotes."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.9  # Higher temperature for more randomness
            )
            
            quote = response.choices[0].message.content.strip()
            logger.info(f"🔴 Generated random quote: {quote[:50]}...")
            logger.debug(f"🔴 Token usage: {response.usage.total_tokens}")
            
            return quote
            
        except Exception as e:
            logger.error(f"Error generating random quote: {e}")
            return "Sorry, I couldn't generate a random quote at the moment. Please try again later."


class QuoteGeneratorExecutor(AgentExecutor):
    """Executor for the Quote Generator Agent following a2a_simple pattern."""

    def __init__(self):
        self.agent = QuoteGenerator()

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        """Execute the quote generation based on the user's request."""
        try:
            # Extract the user message text
            user_message = self._extract_user_message(context)
            logger.info(f"📝 Processing request: '{user_message}'")
            
            # Determine which quote generation method to use
            if self._is_random_request(user_message):
                logger.info("🎯 Routing to random quote generation")
                result = await self.agent.random_quote()
            else:
                # Extract topic from the message
                topic = self._extract_topic(user_message)
                logger.info(f"🎯 Routing to topic quote generation: '{topic}'")
                result = await self.agent.generate_quote(topic)
            
            # Send the result back via event queue
            await event_queue.enqueue_event(new_agent_text_message(result))
            logger.info("✅ Quote generation completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Error in quote generation: {e}")
            error_message = f"Sorry, I encountered an error while generating your quote: {str(e)}"
            await event_queue.enqueue_event(new_agent_text_message(error_message))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        """Cancel the quote generation - not supported."""
        logger.warning("⚠️ Cancel operation requested but not supported")
        raise Exception("Cancel not supported for quote generation")
    
    def _extract_user_message(self, context: RequestContext) -> str:
        """Extract the text message from the request context."""
        try:
            # Try different ways to access the message
            
            # Method 1: Direct access to message parts
            if hasattr(context, 'request') and hasattr(context.request, 'params'):
                params = context.request.params
                if hasattr(params, 'message'):
                    message = params.message
                    if hasattr(message, 'parts') and message.parts:
                        first_part = message.parts[0]
                        if hasattr(first_part, 'root') and hasattr(first_part.root, 'text'):
                            return first_part.root.text
            
            # Method 2: Check if it's a different structure
            if hasattr(context, 'message'):
                message = context.message
                if hasattr(message, 'parts') and message.parts:
                    first_part = message.parts[0]
                    if hasattr(first_part, 'root') and hasattr(first_part.root, 'text'):
                        return first_part.root.text
            
            # Method 3: Check if the text is directly available
            if hasattr(context, 'text'):
                return context.text
            
            # Method 4: Try to get from request body
            if hasattr(context, 'request') and hasattr(context.request, 'body'):
                body = context.request.body
                if hasattr(body, 'message') and hasattr(body.message, 'parts'):
                    first_part = body.message.parts[0]
                    if hasattr(first_part, 'root') and hasattr(first_part.root, 'text'):
                        return first_part.root.text
            
            # Log what we actually have for debugging
            logger.warning(f"⚠️ Could not extract message. Context type: {type(context)}")
            if hasattr(context, 'request'):
                logger.warning(f"⚠️ Request type: {type(context.request)}")
                if hasattr(context.request, 'params'):
                    logger.warning(f"⚠️ Params: {context.request.params}")
            
            # Fallback - return a default message
            return "Generate an inspirational quote"
            
        except Exception as e:
            logger.warning(f"⚠️ Could not extract user message: {e}")
            return "Generate an inspirational quote"
    
    def _is_random_request(self, text: str) -> bool:
        """Determine if the request is for a random quote."""
        text_lower = text.lower().strip()
        random_keywords = ["random", "surprise", "any topic", "choose"]
        return any(keyword in text_lower for keyword in random_keywords)
    
    def _extract_topic(self, text: str) -> str:
        """Extract the topic from the user's message."""
        text_lower = text.lower().strip()
        
        # Try to extract topic after "about"
        if "about" in text_lower:
            parts = text_lower.split("about", 1)
            if len(parts) > 1:
                topic = parts[1].strip().rstrip("?.")
                if topic:
                    return topic
        
        # Try to extract topic from quote request
        if "quote" in text_lower:
            # Remove "quote" and common words to get the topic
            topic = text_lower.replace("quote", "").replace("generate", "").replace("create", "").replace("give me", "").strip()
            if topic and len(topic) > 2:
                return topic
        
        # Default topic
        return "general inspiration" 