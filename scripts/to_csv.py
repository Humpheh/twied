from pymongo import MongoClient
import csv
import ftfy

# Connect to the database
client = MongoClient(host="144.173.8.69")
db = client.HWtwitter

# Get the fields that are to be saved
cursor = db.brexit.find({}, {
    'id_str': 1,
    'text': 1,
    'created_at': 1,
    'retweeted_status.text': 1,
    'timestamp_ms': 1
})

count = 0

# Open the file to output the data to
with open('out.csv', 'w', newline='', encoding='utf-8') as csvfile:

    # Setup the CSV writer and the field names
    fieldnames = ['mongo_id', 'tweet_id', 'text', 'created_at', 'timestamp', 'rt_text']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, dialect=csv.excel)
    writer.writeheader()

    for doc in cursor:
        # Create a dictionary of values based on the field names
        csv_input = {
            'mongo_id': str(doc['_id']),
            'tweet_id': doc['id_str'],
            'text': ftfy.fix_text(doc['text']),
            'created_at': doc['created_at'],
            'timestamp': doc['timestamp_ms'],
            'rt_text': ftfy.fix_text(doc.get('retweeted_status', {'text':''})['text'])
        }

        # Write the dictionary as a new row
        writer.writerow(csv_input)
        count += 1

        if count % 100 == 0:
            print("[+] Processed", count, "tweets.")

        if count >= 10000:
            break
