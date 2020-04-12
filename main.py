import os
from typing import List
import time
import logging

from twitter import Api
from slack import WebClient

logger = logging.getLogger(__name__)


def get_channel_id(slack_client: WebClient, slack_channel: str):
    response = slack_client.conversations_list(limit=1000)
    for channel in response["channels"]:
        if channel.get("name") == slack_channel:
            return channel.get("id")


def pull_and_post(
    consumer_key: str,
    consumer_secret: str,
    access_token: str,
    access_token_secret: str,
    slack_token: str,
    slack_channel: str,
    wait_time: int,
):

    twitter_api = Api(consumer_key, consumer_secret, access_token, access_token_secret)

    slack_client = WebClient(slack_token)
    channel_id = get_channel_id(slack_client, slack_channel)

    since_id = None
    while True:
        previous_posts = set()
        statuses = twitter_api.GetHomeTimeline(since_id=since_id)

        if statuses:
            if channel_id is not None:
                history = slack_client.channels_history(channel=channel_id, count=20)
                for message in history.get("messages"):
                    previous_post = message.get("text")
                    previous_posts.add(previous_post.strip("<>"))

            logger.info(f"Got {len(statuses)} posts from Twitter.")
            for status in reversed(statuses):
                user = status.user
                slack_post_text = (
                    f"http://twitter.com/{user.screen_name}/status/{status.id}"
                )

                if slack_post_text not in previous_posts:
                    slack_client.chat_postMessage(
                        text=slack_post_text,
                        channel=slack_channel,
                        icon_url=user.profile_image_url,
                        username=user.name,
                    )
                    since_id = status.id
                    logger.info(f"Posted status from {user.name} to {slack_channel}.")
                    time.sleep(5)  # give slack time to format the posts

                else:
                    logger.info(
                        f"Status from {user.name} already in {slack_channel}, skipping."
                    )

        else:
            logger.info(f"No new twitter posts.")
        time.sleep(wait_time)


def _retrieve_keys() -> List[str]:
    env_vars = (
        "TWITTER_CONSUMER_KEY",
        "TWITTER_CONSUMER_SECRET",
        "TWITTER_ACCESS_TOKEN",
        "TWITTER_ACCESS_TOKEN_SECRET",
        "SLACK_API_TOKEN",
        "TWITTER_ON_SLACK_CHANNEL",
    )

    keys = []

    for env_var in env_vars:
        value = os.environ.get(env_var)
        if value is None:
            raise IOError(f"Missing required env var: {env_var}")

        keys.append(value)
    return keys


def main(wait_time: int = 60):
    keys = _retrieve_keys()
    pull_and_post(*keys, wait_time=wait_time)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(asctime)s %(message)s",
        datefmt="%m-%d %H:%M:%S",
    )
    main()
