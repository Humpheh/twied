"""import shapefile

sf = shapefile.Reader("D:/ds/gadm/gadm28")

for i in sf.iterShapes():
    print (dir(i))

from osgeo import ogr

daShapefile = r"D:/ds/gadm/gadm28.shp"

dataSource = ogr.Open(daShapefile)
daLayer = dataSource.GetLayer(0)
layerDefinition = daLayer.GetLayerDefn()


for i in range(layerDefinition.GetFieldCount()):
    print (layerDefinition.GetFieldDefn(i).GetName())"""

# -*- coding: utf-8 -*-

def str_or_none(st):
    if st == None:
        return None
    return str(st)

import sqlite3
conn = sqlite3.connect('polydb.db')

c = conn.cursor()
c.execute('''CREATE TABLE gadm (n1 TEXT COLLATE NOCASE, n2 TEXT COLLATE NOCASE, n3 TEXT COLLATE NOCASE, n4 TEXT COLLATE NOCASE, n5 TEXT COLLATE NOCASE, poly BLOB)''')
for i in range(1, 6):
    c.execute('CREATE INDEX gadm' + str(i) + ' ON gadm (n' + str(i) + ')')
conn.commit()

import fiona
fi = fiona.open(r"D:/ds/gadm/gadm28.shp", 'r')

count = 0
while True:
    try:
        a = fi.next()
    except:
        break

    count += 1
    c.execute("INSERT INTO gadm VALUES (:n1, :n2, :n3, :n4, :n5, :poly)", {
        'n1': str_or_none(a['properties']['NAME_1']),
        'n2': str_or_none(a['properties']['NAME_2']),
        'n3': str_or_none(a['properties']['NAME_3']),
        'n4': str_or_none(a['properties']['NAME_4']),
        'n5': str_or_none(a['properties']['NAME_5']),
        'poly': str_or_none(a['geometry'])
    })

    print (count)

conn.commit()

print (count)
