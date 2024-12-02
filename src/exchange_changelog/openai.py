import functools
import os
from collections.abc import Iterable
from typing import TypeVar

from loguru import logger
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


@functools.cache
def get_openai_client() -> OpenAI:
    return OpenAI()


@functools.cache
def get_openai_model() -> str:
    model = os.getenv("OPENAI_MODEL")
    if not model:
        logger.warning("OPENAI_MODEL environment variable is not set, using gpt-4o-mini")
        return "gpt-4o-mini"
    return model


def create_completion(messages: Iterable[ChatCompletionMessageParam]) -> str:
    client: OpenAI = get_openai_client()
    model = get_openai_model()
    temperature = float(os.getenv("OPENAI_TEMPERATURE", 0))

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


def parse_completion(messages: Iterable[ChatCompletionMessageParam], response_format: type[T]) -> T:
    client: OpenAI = get_openai_client()
    model = get_openai_model()
    temperature = float(os.getenv("OPENAI_TEMPERATURE", 0))

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
