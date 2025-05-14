import base64
import os
from pathlib import Path

import logfire
import nest_asyncio
import yaml
from loguru import logger


def load_yaml(f: str | Path) -> dict:
    path = Path(f)
    if not path.exists():
        raise FileNotFoundError(f"File {path} does not exist")

    with path.open(encoding="utf-8") as fp:
        return yaml.safe_load(fp)


def configure_langfuse(service_name: str | None = None) -> None:
    """Configure OpenTelemetry with Langfuse authentication.

    https://langfuse.com/docs/integrations/openaiagentssdk/openai-agents
    """
    logger.info("Configuring OpenTelemetry with Langfuse...")

    public_key = os.environ.get("LANGFUSE_PUBLIC_KEY")
    if public_key is None:
        logger.warning("LANGFUSE_PUBLIC_KEY is not set. Skipping Langfuse configuration.")
        return

    secret_key = os.environ.get("LANGFUSE_SECRET_KEY")
    if secret_key is None:
        logger.warning("LANGFUSE_SECRET_KEY is not set. Skipping Langfuse configuration.")
        return

    host = os.environ.get("LANGFUSE_HOST")
    if host is None:
        logger.warning("LANGFUSE_HOST is not set. Skipping Langfuse configuration.")
        return

    # Build Basic Auth header.
    langfuse_auth = base64.b64encode(f"{public_key}:{secret_key}".encode()).decode()

    # Configure OpenTelemetry endpoint & headers
    os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = host + "/api/public/otel"
    os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {langfuse_auth}"

    nest_asyncio.apply()

    logger.info("Configuring Logfire...")
    logfire.configure(
        service_name=service_name,
        send_to_logfire=False,
    )
    logfire.instrument_openai_agents()
