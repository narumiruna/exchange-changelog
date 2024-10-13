import functools
import os
from typing import Literal
from typing import TypedDict

from loguru import logger
from openai import OpenAI

MAX_CONTENT_LENGTH = 1_048_576


class Message(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: str


@functools.cache
def get_openai_client() -> OpenAI():
    return OpenAI()


@functools.cache
def get_openai_model() -> str:
    model = os.getenv("OPENAI_MODEL")
    if not model:
        logger.warning("OPENAI_MODEL environment variable is not set, using gpt-4o-mini")
        return "gpt-4o-mini"
    return model


def create_completion(messages: list[Message]) -> str:
    client: OpenAI = get_openai_client()
    model = get_openai_model()
    temperature = float(os.getenv("OPENAI_TEMPERATURE", 0))

    for message in messages:
        message["content"] = message["content"][:MAX_CONTENT_LENGTH]

    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    if not completion.choices:
        raise ValueError("No completion choices returned")

    content = completion.choices[0].message.content
    if not content:
        raise ValueError("No completion message content")

    return content


def parse_completion(messages: list[Message], response_format):
    client: OpenAI = get_openai_client()
    model = get_openai_model()
    temperature = float(os.getenv("OPENAI_TEMPERATURE", 0))

    for message in messages:
        message["content"] = message["content"][:MAX_CONTENT_LENGTH]

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=messages,
        temperature=temperature,
        response_format=response_format,
    )

    if not completion.choices:
        raise ValueError("No completion choices returned")

    parsed = completion.choices[0].message.parsed
    if not parsed:
        raise ValueError("No parsed response")

    return parsed
