from twitter import Api, Status


def main(consumer_key: str, consumer_secret: str, access_token: str, access_token_secret: str):

    twitter_api = Api(consumer_key,
                      consumer_secret,
                      access_token,
                      access_token_secret,
                      application_only_auth=True)


