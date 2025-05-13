from __future__ import annotations

import os
from functools import cache
from typing import Literal
from typing import TypeVar

from agents import Agent
from agents import Model
from agents import ModelSettings
from agents import OpenAIChatCompletionsModel
from agents import OpenAIResponsesModel
from agents import Runner
from loguru import logger
from openai import AsyncAzureOpenAI
from openai import AsyncOpenAI
from openai.types import ChatModel

T = TypeVar("T")


@cache
def get_openai_client() -> AsyncOpenAI:
    # Azure OpenAI-comatible endpoints
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    if azure_api_key:
        logger.info("Using Azure OpenAI API key")
        return AsyncAzureOpenAI(api_key=azure_api_key)

    logger.info("Using OpenAI API key")
    return AsyncOpenAI()


@cache
def get_openai_model(
    model: ChatModel | str | None = None,
    api_type: Literal["responses", "chat_completions"] = "responses",
) -> Model:
    if model is None:
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    openai_client = get_openai_client()

    match api_type:
        case "responses":
            return OpenAIResponsesModel(model, openai_client=openai_client)
        case "chat_completions":
            return OpenAIChatCompletionsModel(model, openai_client=openai_client)
        case _:
            raise ValueError(f"Invalid API type: {api_type}. Use 'responses' or 'chat_completions'.")


@cache
def get_openai_model_settings():
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    temperature = None if model == "o3-mini" else float(os.getenv("OPENAI_TEMPERATURE", 0.0))
    return ModelSettings(temperature=temperature)


def _create_agent(
    instructions: str | None = None,
    name: str = "lazy_run",
    model: Model | None = None,
    model_settings: ModelSettings | None = None,
    output_type: type[T] | None = None,
) -> Agent:
    model = model or get_openai_model()
    model_settings = model_settings or ModelSettings()
    return Agent(
        name=name,
        instructions=instructions,
        model=model,
        model_settings=model_settings,
        output_type=output_type,
    )


async def lazy_run(
    input: str,
    instructions: str | None = None,
    name: str = "lazy_run",
    model: Model | None = None,
    model_settings: ModelSettings | None = None,
    output_type: type[T] | None = None,
) -> T:
    """Run the agent with the given input and instructions.

    Args:
        input (str): The input to the agent.
        instructions (str | None): The instructions for the agent.
        name (str): The name of the agent.
        model (Model | None): The model to use for the agent.
        model_settings (ModelSettings | None): The settings for the model.
        output_type (type[T] | None): The type of output to return.
    """
    model_settings = model_settings or ModelSettings()
    result = await Runner.run(
        starting_agent=_create_agent(
            instructions=instructions,
            name=name,
            model=model,
            model_settings=model_settings,
            output_type=output_type,
        ),
        input=input,
    )

    if output_type is None:
        return result.final_output
    return result.final_output_as(output_type)


def lazy_run_sync(
    input: str,
    instructions: str | None = None,
    name: str = "lazy_run_sync",
    model: Model | None = None,
    model_settings: ModelSettings | None = None,
    output_type: type[T] | None = None,
) -> str | T:
    """Run the agent with the given input and instructions.

    Args:
        input (str): The input to the agent.
        instructions (str | None): The instructions for the agent.
        name (str): The name of the agent.
        model (Model | None): The model to use for the agent.
        model_settings (ModelSettings | None): The settings for the model.
        output_type (type[T] | None): The type of output to return.
    """
    model_settings = model_settings or ModelSettings()
    result = Runner.run_sync(
        starting_agent=_create_agent(
            instructions=instructions,
            name=name,
            model=model,
            model_settings=model_settings,
            output_type=output_type,
        ),
        input=input,
    )

    if output_type is None:
        return result.final_output
    return result.final_output_as(output_type)
