from twitter import Api, Status
import os
from typing import List


def pull_and_post(
    consumer_key: str, consumer_secret: str, access_token: str, access_token_secret: str
):

    twitter_api = Api(
        consumer_key,
        consumer_secret,
        access_token,
        access_token_secret,
        application_only_auth=True,
    )


def _retrieve_keys() -> List[str]:
    env_vars = (
        "TWITTER_CONSUMER_KEY",
        "TWITTER_CONSUMER_SECRET",
        "TWITTER_ACCESS_TOKEN",
        "TWITTER_ACCESS_TOKEN_SECRET",
    )

    keys = []

    for env_var in env_vars:
        value = os.environ.get(env_var)
        if value is None:
            raise IOError(f"Missing required env var: {env_var}")

        keys.append(value)
    return keys


def main():
    keys = _retrieve_keys()
    pull_and_post(*keys)
