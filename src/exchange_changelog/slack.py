import os
from functools import cache

from loguru import logger
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


@cache
def get_slack_client() -> WebClient | None:
    token = os.getenv("SLACK_TOKEN")
    if token is None:
        logger.warning("SLACK_TOKEN environment variable is not set")
        return None

    return WebClient(token=token)


@cache
def get_slack_channel() -> str | None:
    channel = os.getenv("SLACK_CHANNEL")
    if channel is None:
        logger.warning("SLACK_CHANNEL environment variable is not set")
        return None

    return channel


def post_slack_message(*, text: str | None = None, blocks=None) -> None:
    channel = get_slack_channel()
    client = get_slack_client()

    if channel is None or client is None:
        return

    try:
        client.chat_postMessage(channel=channel, blocks=blocks, text=text, mrkdwn=True)
    except SlackApiError as e:
        logger.error("slack api error: {}", e)
