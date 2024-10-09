import functools
import os

from dotenv import find_dotenv
from dotenv import load_dotenv
from loguru import logger
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv(find_dotenv())


@functools.cache
def get_slack_client() -> WebClient:
    client = WebClient(token=os.getenv("SLACK_TOKEN"))
    return client


def post_slack_message(channel: str, text: str) -> None:
    client = get_slack_client()
    try:
        client.chat_postMessage(channel=channel, text=text)
    except SlackApiError as e:
        logger.error("slack api error: {}", e)
