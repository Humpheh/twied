# -*- coding: utf-8 -*-

def str_or_none(st):
    if st == None:
        return None
    return str(st)

import sqlite3
conn = sqlite3.connect('D:/ds/polydb_2.db')

c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS countries (
    name TEXT COLLATE NOCASE,
    poly BLOB,
    fips TEXT,
    iso2 TEXT,
    iso3 TEXT,
    un INT,
    area INT,
    lon REAL,
    lat REAL
)''')
c.execute('CREATE INDEX IF NOT EXISTS countryname ON countries (name)')
conn.commit()

import fiona
fi = fiona.open(r"D:/ds/tm_world/TM_WORLD_BORDERS-0.3.shp", 'r')

count = 0
while True:
    try:
        a = fi.next()
    except:
        break

    di = a['properties']
    di['poly'] = str(a['geometry'])

    count += 1
    c.execute("INSERT INTO countries VALUES (:NAME, :poly, :FIPS, :ISO2, :ISO3, :UN, :AREA, :LON, :LAT)", di)

    print (count)

conn.commit()

print (count)
