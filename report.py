import argparse
import time
import sys
import logging

import twicol
from twython import Twython

twicol.setup_logger(False)

# parse the arguments
parser = argparse.ArgumentParser()
parser.add_argument('--text', help='the text to tweet', type=str, required=True)
parser.add_argument('-m', help='if to @mention', action='store_true')
args = parser.parse_args()

# load the twitter API settings
try:
    api_settings = twicol.config._sections['twitter']
except KeyError:
    logging.error ("Twitter API settings not defined in config")
    sys.exit()

tweet_text = (twicol.config.get("reporting", "mention") + " {0}" if args.m else "{0}").format(args.text)

@twicol.exception_repeat
def send_tweet():
    twicol.send_tweet(api_settings, tweet_text)

send_tweet()

ofile = open('_reportlastud.time', 'w')
ofile.write("{0}".format(time.time()))
ofile.close()

ofile = open('_reportlastud.time', 'r')
print(float(ofile.read()))
ofile.close()

# CHECKS
# 1. Log file growing
# 2. if log above certain size - archive
# 3. Check mongodb still running
