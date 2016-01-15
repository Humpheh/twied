import sys

from twython import Twython
from twicol import *

setup_logger()

# get the twitter API settings
try:
    api_settings = {
        'app_key': '9yfKaZShsFVsH0siyTQl7IjLj',
        'app_secret': 'o1FmDFP8Tb9yZ28s9vhGmcjYfRgog8qm8prWr45wZLDV7xouUb'
    } #config._sections['twitter']
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

searchstr = col_string[1].replace(",", " OR ")
print (searchstr)

from_id = int(input("Enter from id: "))
to_id = int(input("Enter to id: "))

results = twitter.search(q=searchstr, result_type='recent', include_entities=True, count=100, max_id=to_id)#since_id=from_id, )

res = 0
for result in results['statuses']:
    print (result['id'])

    if result['id'] <= from_id:
        done = True
        print ("Breaking")
        break

    res += 1
