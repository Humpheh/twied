import csv
import sqlite3

conn = sqlite3.connect('D:/ds/polydb_2.db')
c = conn.cursor()

with open('D:/ds/tzcodes.csv', newline='') as csvfile:
    oreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in oreader:
        print (row[0], row[1])
        c.execute("UPDATE tz SET code = :code WHERE zone = :zone", {'code':row[1], 'zone':row[0]})

conn.commit()
conn.close()
