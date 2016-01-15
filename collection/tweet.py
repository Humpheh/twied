import logging
from twython import Twython

def send_tweet(api_settings, tweet_text):
    logging.info ("Attempting to connect to Twitter API...")
    twitter = Twython(**api_settings)
    logging.info ("Attemting to send tweet: {0}".format(tweet_text))
    twitter.update_status(status=tweet_text)
    logging.info ("Tweet sent.")
