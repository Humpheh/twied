# -*- coding: utf-8 -*-

def str_or_none(st):
    if st == None:
        return None
    return str(st)

import sqlite3
conn = sqlite3.connect(':memory:')#('D:/ds/polydb_2.db')

c = conn.cursor()
c.execute('CREATE TABLE tz (zone TEXT COLLATE NOCASE, poly BLOB)')
c.execute('CREATE INDEX tzz ON tz (zone)')
conn.commit()

import fiona
fi = fiona.open(r"D:/ds/tz_world/tz_world.shp", 'r')

count = 0
while True:
    try:
        a = fi.next()
    except:
        break

#    print (a['properties']['TZID'])

    a['geometry'] = ''
    print (a)

    count += 1
    c.execute("INSERT INTO tz VALUES (:zone, :poly)", {
        'zone': str_or_none(a['properties']['TZID']),
        'poly': str_or_none(a['geometry'])
    })

    print (count)

conn.commit()

print (count)
