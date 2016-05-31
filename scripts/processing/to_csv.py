from pymongo import MongoClient
import ftfy
import json

# Connect to the database
client = MongoClient(host="144.173.8.69")
db = client.HWtwitter

# Get the fields that are to be saved
cursor = db.brexit.find({}, {
    'id_str': 1,
    'text': 1,
    'created_at': 1,
    'retweeted_status.text': 1,
    'timestamp_ms': 1,
    'retweet_count': 1,
    'favorite_count': 1
})

count = 0

# Open the file to output the data to
with open('out.json', 'w', newline='', encoding='utf-8') as file:

    for doc in cursor:
        # Create a dictionary of values based on the field names
        row_input = {
            'mid': str(doc['_id']),  # mongo id
            'tid': doc['id_str'],  # tweet id
            'text': ftfy.fix_text(doc['text']),
            'date': doc['created_at'],
            'ts': doc['timestamp_ms'],  # timestamp
            'rt_text': ftfy.fix_text(doc.get('retweeted_status', {'text':''})['text']),
            'rtc': doc['retweet_count'],  # retweet count
            'fvc': doc['favorite_count']  # favourite count
        }

        # Write the dictionary as a new row
        file.write(json.dumps(row_input) + "\n")
        count += 1

        if count % 100 == 0:
            print("[+] Processed", count, "tweets.")

        if count >= 10000:
            break
