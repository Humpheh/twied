from pymongo import MongoClient
import re
import sys
import csv

def print_line(line):
    sys.stdout.write("\r" + line)
    sys.stdout.flush()

client = MongoClient()
db = client.twitter
cursor = db.tweets.find()

urld = re.compile('(https?:\/\/)?([\da-z\.-]+\.[a-z\.]{2,6})([\/\w\.-]*)*\/?')

counts = {}

c = 0
d = 0
for doc in cursor:
    for url in doc['entities']['urls']:
        matches = urld.findall(url['display_url'])
        for i in matches:
            try:
                counts[i[1]] += 1
            except:
                counts[i[1]] = 1

            c += 1
            if c % 1000 == 0:
                print_line ("Processed " + str(c) + " urls, " + str(d) + " documents.")
    d += 1
print ('')

countlist = []
for key, value in counts.items():
    countlist.append((key, value))

print ("Sorting hashtags...")
countlist.sort(key=lambda x: x[1], reverse=True)

print ("Outputting to files...")
with open('websitecount.csv', 'w', newline='', encoding='utf-8') as csvfile:
    topposters = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)

    for i in countlist:
        name = i[0]
        topposters.writerow([name, i[1]])
