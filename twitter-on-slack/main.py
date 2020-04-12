from twitter import Api
from slack import WebClient
import os
from typing import List
import time
import logging
from tqdm import trange

logger = logging.getLogger(__name__)


def pull_and_post(
    consumer_key: str,
    consumer_secret: str,
    access_token: str,
    access_token_secret: str,
    slack_token: str,
    slack_channel: str,
    wait_time: int = 60,
):

    twitter_api = Api(
        consumer_key,
        consumer_secret,
        access_token,
        access_token_secret,
        application_only_auth=True,
    )

    slack_client = WebClient(slack_token)
    since_id = None

    while True:
        statuses = twitter_api.GetHomeTimeline(since_id=since_id)
        logger.info(f"Got {len(statuses)} posts from Twitter.")

        for status in statuses:
            user = status.user
            slack_client.chat_postMessage(
                text=f"http://twitter.com/{user.name}/status/{status.id}",
                channel=slack_channel,
                icon_url=user.profile_image_url,
                username=user.name,
            )
            since_id = status.id
            logger.info(f"Posted status from {user.name} to {slack_channel}.")

        for _ in trange(wait_time, desc="Time to sleep 😴"):
            time.sleep(1)


def _retrieve_keys() -> List[str]:
    env_vars = (
        "TWITTER_CONSUMER_KEY",
        "TWITTER_CONSUMER_SECRET",
        "TWITTER_ACCESS_TOKEN",
        "TWITTER_ACCESS_TOKEN_SECRET",
        "SLACK_API_TOKEN",
    )

    keys = []

    for env_var in env_vars:
        value = os.environ.get(env_var)
        if value is None:
            raise IOError(f"Missing required env var: {env_var}")

        keys.append(value)
    return keys


def main(slack_channel: str, wait_time: int):
    keys = _retrieve_keys()
    pull_and_post(*keys, slack_channel=slack_channel, wait_time=wait_time)
