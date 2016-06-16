import configparser
import time

from twython import Twython, TwythonError
from pymongo import MongoClient
from urllib3.exceptions import MaxRetryError

from twied.multiind.inference import InferThread
from twied.multiind.indicators.locfieldindicator import GeonamesException
from twied.multiind.interfaces.webinterfaces import GeonamesDecodeException

# Setup configuration file
config = configparser.ConfigParser()
config.read("settings.ini")

# Connect to the MongoDB (database twitter, collection tweets)
client = MongoClient("localhost", 27017)
col = client["twitter"]["tweets"]

# Query used for selecting tweets, empty because target is all tweets
query = {}

# Setup a Twython object to tweet error message if problem
api_settings = config._sections['twitter']
twitter = Twython(**api_settings)


# Function for tweeting message if there is an error
def tweetstr(string):
    global twitter
    try:
        print("[!] Attemting to send tweet: {0}".format(string))
        twitter.update_status(status=string)
        print("[+] Tweet sent.")
    except Exception:
        return


# Name of inference task
inf_name = "MyCol"

# Name of the field to save the result to
field = "inf"

# Run the inference
inf = InferThread(col, config, inf_id=inf_name, tweetfunc=tweetstr, tweetint=5000, proc_id=1)
while True:
    print("[+] Starting inference...")
    try:
        inf.infer(query, field=field)
        print("[!] Inference finished successfully.")
        tweetstr("@Humpheh %s - finished successfully." % inf_name)
        break
    except MaxRetryError:
        print("[!] Got a MaxRetryError - sleeping for 2 mins...")
        time.sleep(2 * 60)  # sleep for 5 mins
    except GeonamesException:
        print("[!] Got a GeonamesException - sleeping for 10 mins...")
        time.sleep(10 * 60)  # sleep for 10 mins
    except GeonamesDecodeException:
        print("[!] Got a GeonamesDecodeException - sleeping for 2 mins...")
        time.sleep(2 * 60)  # sleep for 2 mins
    except TwythonError:
        break
    except Exception as e:
        print("[!] Exception caught")
        tweetstr("@Humpheh %s - exited due to a %s." % (inf_name, type(e).__name__))
        raise
