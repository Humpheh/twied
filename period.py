import sys

from twython import Twython
from twicol import *

setup_logger()

# get the twitter API settings
try:
    api_settings = config._sections['twitter']
except KeyError:
    logging.critical("Twitter API settings not defined in config")
    sys.exit()

twitter = Twython(**api_settings)

col_items = config.items("collections")
col_string = None
while col_string == None:
    i = 1
    cols = []
    for key, string in col_items:
        print (i, ':', key, string)
        cols.append((key, string))
        i += 1

    col_id = int(input("Enter ID of colection: "))
    if col_id > 0 and col_id <= i:
        col_string = cols[col_id-1]
    else:
        print("Invalid collection id..")

from_id = int(input("Enter from id:"))
to_id = int(input("Enter to id:"))

results = twitter.cursor(twitter.search, q=col_string[1], since_id=from_id, max_id=to_id)
for result in results:
    print (result['id_str'])
