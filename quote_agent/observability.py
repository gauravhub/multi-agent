"""
Observability configuration for the Quote Agent using Langfuse and OpenInference.
"""

import os
import logging
from typing import Optional
from langfuse import Langfuse
from openinference.instrumentation.openai import OpenAIInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

logger = logging.getLogger(__name__)

# Global Langfuse client instance
langfuse_client: Optional[Langfuse] = None

def setup_observability() -> Optional[Langfuse]:
    """
    Set up observability with Langfuse and OpenInference instrumentation.
    
    Returns:
        Langfuse client instance if enabled, None otherwise
    """
    global langfuse_client
    
    # Check if observability is enabled
    if not _is_observability_enabled():
        logger.info("📊 Observability is disabled")
        return None
    
    try:
        # Initialize Langfuse
        langfuse_client = _setup_langfuse()
        
        # Set up OpenTelemetry
        _setup_opentelemetry()
        
        # Instrument OpenAI
        _setup_openai_instrumentation()
        
        logger.info("✅ Observability setup completed successfully")
        return langfuse_client
        
    except Exception as e:
        logger.error(f"❌ Failed to setup observability: {e}")
        return None

def _is_observability_enabled() -> bool:
    """Check if observability is enabled via environment variable."""
    return os.getenv("LANGFUSE_ENABLED", "false").lower() == "true"

def _setup_langfuse() -> Langfuse:
    """Initialize Langfuse client."""
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    
    if not secret_key or not public_key:
        raise ValueError("LANGFUSE_SECRET_KEY and LANGFUSE_PUBLIC_KEY must be set")
    
    client = Langfuse(
        secret_key=secret_key,
        public_key=public_key,
        host=host
    )
    
    logger.info(f"🔍 Langfuse initialized with host: {host}")
    return client

def _setup_opentelemetry():
    """Set up OpenTelemetry tracing."""
    service_name = os.getenv("OTEL_SERVICE_NAME", "quote-agent")
    service_version = os.getenv("OTEL_SERVICE_VERSION", "1.0.0")
    
    # Create resource
    resource = Resource.create({
        "service.name": service_name,
        "service.version": service_version,
    })
    
    # Set up tracer provider
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)
    
    # Set up OTLP exporter (optional - for external tracing systems)
    langfuse_host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    otlp_endpoint = f"{langfuse_host}/api/public/ingestion"
    
    try:
        otlp_exporter = OTLPSpanExporter(
            endpoint=otlp_endpoint,
            headers={
                "Authorization": f"Bearer {os.getenv('LANGFUSE_PUBLIC_KEY')}",
            }
        )
        span_processor = BatchSpanProcessor(otlp_exporter)
        tracer_provider.add_span_processor(span_processor)
        logger.info("🔄 OpenTelemetry OTLP exporter configured")
    except Exception as e:
        logger.warning(f"⚠️ Could not setup OTLP exporter: {e}")

def _setup_openai_instrumentation():
    """Set up OpenAI instrumentation with OpenInference."""
    OpenAIInstrumentor().instrument()
    logger.info("🤖 OpenAI instrumentation enabled")

def get_langfuse_client() -> Optional[Langfuse]:
    """Get the global Langfuse client instance."""
    return langfuse_client

def create_trace(name: str, **kwargs):
    """
    Create a Langfuse trace for monitoring agent operations.
    
    Args:
        name: Name of the trace
        **kwargs: Additional trace metadata
        
    Returns:
        Langfuse trace object or None if observability is disabled
    """
    if not langfuse_client:
        return None
    
    try:
        return langfuse_client.trace(name=name, **kwargs)
    except Exception as e:
        logger.error(f"❌ Failed to create trace: {e}")
        return None

def create_generation(trace, name: str, **kwargs):
    """
    Create a Langfuse generation for monitoring LLM calls.
    
    Args:
        trace: Parent trace object
        name: Name of the generation
        **kwargs: Additional generation metadata
        
    Returns:
        Langfuse generation object or None if observability is disabled
    """
    if not trace:
        return None
    
    try:
        return trace.generation(name=name, **kwargs)
    except Exception as e:
        logger.error(f"❌ Failed to create generation: {e}")
        return None

def flush_observability():
    """Flush any pending observability data."""
    if langfuse_client:
        try:
            langfuse_client.flush()
            logger.info("📤 Observability data flushed")
        except Exception as e:
            logger.error(f"❌ Failed to flush observability data: {e}")

def shutdown_observability():
    """Shutdown observability and cleanup resources."""
    global langfuse_client
    
    if langfuse_client:
        try:
            langfuse_client.flush()
            langfuse_client = None
            logger.info("🔌 Observability shutdown completed")
        except Exception as e:
            logger.error(f"❌ Failed to shutdown observability: {e}") 