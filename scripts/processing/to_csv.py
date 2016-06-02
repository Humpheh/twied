from pymongo import MongoClient
import ftfy
import json

# Connect to the database
client = MongoClient()  # host="144.173.8.69")
db = client.HWtwitter

# Get the fields that are to be saved
cursor = db.brexit.find({}, {
    'id_str': 1,
    'text': 1,
    'created_at': 1,
    'retweeted_status.text': 1,
    'retweeted_status.user.screen_name': 1,
    'timestamp_ms': 1,
    'entities': 1,
    'user.screen_name': 1
})


def open_file(id):
    return open('out_%i.json' % id, 'w', newline='', encoding='utf-8')


# Open the file to output the data to
file_id = 0
file = open_file(file_id)

count = 0
for doc in cursor:
    # Create a dictionary of values based on the field names
    row_input = {
        'mid': str(doc['_id']),  # mongo id
        'tid': doc['id_str'],  # tweet id
        'text': ftfy.fix_text(doc['text']),
        'date': doc['created_at'],
        'ts': doc['timestamp_ms'],  # timestamp
        'rt_text': ftfy.fix_text(doc.get('retweeted_status', {'text': ''})['text']),
        'rt_user': doc.get('retweeted_status', {'user': {'screen_name': ''}})['user']['screen_name'],
        'user': doc['user']['screen_name'],  # the user
        'hashtags': [t['text'] for t in doc['entities']['hashtags']],
        'urls': [t['expanded_url'] for t in doc['entities']['urls']],
        'mentions': [t['screen_name'] for t in doc['entities']['user_mentions']],
    }

    # Write the dictionary as a new row
    file.write(json.dumps(row_input) + "\n")
    count += 1

    if count % 10000 == 0:
        print("[+] Processed", count, "tweets.")

    if count % 1000000 == 0:
        print("[#] Splitting to new file: %i" % file_id)
        file.close()
        file_id += 1
        file = open_file(file_id)

    #if count >= 1000:
    #    del cursor
    #    break

file.close()