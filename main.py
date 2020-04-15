import os
from typing import List, Optional, Dict, Any
import time
import logging

from twitter import Api, Status
from slack import WebClient

logger = logging.getLogger(__name__)


def pull_and_publish(
    consumer_key: str,
    consumer_secret: str,
    access_token: str,
    access_token_secret: str,
    slack_token: str,
    slack_channel: str,
    wait_time: int,
):
    """Continuously pull recent Twitter statuses and publish them to Slack."""

    twitter_api = Api(consumer_key, consumer_secret, access_token, access_token_secret)

    slack_client = WebClient(slack_token)
    channel_id = _get_channel_id(slack_client, slack_channel)

    since_id = None
    while True:
        statuses = twitter_api.GetHomeTimeline(since_id=since_id)

        if statuses:
            logger.info(f"Got {len(statuses)} posts from Twitter.")
            since_id = post_to_slack(
                channel_id, since_id, slack_channel, slack_client, statuses
            )
        else:
            logger.info("No new twitter posts.")

        time.sleep(wait_time)


def _get_channel_id(slack_client: WebClient, slack_channel: str) -> str:
    """Retrieves the corresponding channel ID to slack_channel."""
    response = slack_client.conversations_list(limit=1000)
    for channel in response["channels"]:
        if channel.get("name") == slack_channel:
            return channel.get("id")


def post_to_slack(
    channel_id: Optional[str],
    since_id: Optional[int],
    slack_channel: str,
    slack_client: WebClient,
    statuses: List[Status],
) -> int:
    """Post statuses to slack if they aren't already in the channel."""
    previous_posts = set()

    if channel_id is not None:
        history = slack_client.channels_history(channel=channel_id, count=100)
        for message in history.get("messages"):
            previous_post = message.get("text")
            previous_posts.add(previous_post)

    for status in reversed(statuses):
        user = status.user
        slack_post_text = (
            f"<Link to tweet|http://twitter.com/{user.screen_name}/status/{status.id}>"
        )

        if slack_post_text not in previous_posts:
            slack_client.chat_postMessage(
                blocks=[markdown_block(slack_post_text)],
                channel=slack_channel,
                icon_url=user.profile_image_url,
                username=user.name,
            )
            logger.info(
                f"Posted status from {user.name} to slack on `#{slack_channel}`."
            )
            time.sleep(5)  # give slack time to format the posts

        else:
            logger.info(
                f"Status from {user.name} already in '{slack_channel}', skipping slack post."
            )

        since_id = status.id

    return since_id


def markdown_block(text: str) -> Dict[str, Any]:
    """Creates a simple message block using Slack's block format."""
    return {
        "type": "section",
        "text": {"type": "mrkdwn", "text": text},
    }


def _retrieve_keys() -> List[str]:
    """Retrieve the necessary keys to communicate with Twitter and Slack APIs."""
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


def main(wait_time: int = 120):
    """Continuously pull twitter posts and publish them to a slack channel."""
    keys = _retrieve_keys()

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(asctime)s %(message)s",
        datefmt="%m-%d %H:%M:%S",
    )
    pull_and_publish(*keys, wait_time=wait_time)


if __name__ == "__main__":
    main()
