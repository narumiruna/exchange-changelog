import os

from dotenv import find_dotenv
from dotenv import load_dotenv
from loguru import logger
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv(find_dotenv())


def post_slack_message(text: str) -> None:
    token = os.getenv("SLACK_TOKEN")
    if token is None:
        logger.info("slack token not found")
        return

    channel = os.getenv("SLACK_CHANNEL")
    if channel is None:
        logger.info("slack channel not found")
        return

    client = client = WebClient(token=token)
    try:
        client.chat_postMessage(channel=channel, text=text, mrkdwn=True)
    except SlackApiError as e:
        logger.error("slack api error: {}", e)
