import sqlite3
import ast
import re

class GADMPolyInterface:
    def __init__(self, dbloc):
        self.conn = sqlite3.connect(dbloc)
        self.c = self.conn.cursor()
        orstr = " or ".join(['n{0} = :n{0}'.format(i) for i in range(1, 6)])
        self.qstring = "SELECT poly FROM gadm WHERE " + orstr

    def get_polys(self, name):
        self.c.execute(self.qstring, {
            'n1': name, 'n2': name, 'n3': name, 'n4': name, 'n5': name,
        })

        allpolys = []
        polys = self.c.fetchall()
        for i in polys:
            ji = ast.literal_eval(i[0])
            for p in ji['coordinates']:
                if isinstance(p[0], list):
                    allpolys += p
                else:
                    allpolys.append(p)
        return allpolys

    def destroy(self):
        self.conn.close()


class CountryPolyInterface:
    def __init__(self, dbloc):
        self.conn = sqlite3.connect(dbloc)
        self.c = self.conn.cursor()
        self.qstring = "SELECT poly FROM countries WHERE name LIKE :name"

    def get_polys(self, name):
        self.c.execute(self.qstring, { 'name': name })
        allpolys = []
        polys = self.c.fetchall()
        for i in polys:
            ji = ast.literal_eval(i[0])
            for p in ji['coordinates']:
                if isinstance(p[0], list):
                    allpolys += p
                else:
                    allpolys.append(p)
        return allpolys

    def destroy(self):
        self.conn.close()

class TZPolyInterface:
    def __init__(self, dbloc):
        self.conn = sqlite3.connect(dbloc)
        self.c = self.conn.cursor()
        self.qstring = "SELECT poly FROM tz WHERE zone LIKE :zone"
        self.qstringoff = "SELECT poly FROM tz WHERE offset LIKE :offset"
        self.qstringamerica = "SELECT poly FROM tz WHERE zone LIKE :zone AND code = :code"

    def proc_polys(self, polys):
        allpolys = []
        for i in polys:
            ji = ast.literal_eval(i[0])
            for p in ji['coordinates']:
                if isinstance(p[0], list):
                    allpolys += p
                else:
                    allpolys.append(p)
        return allpolys

    def get_polys(self, name):
        # add processing
        self.c.execute(self.qstring, { 'zone': "%" + name + "%" })
        return self.proc_polys(self.c.fetchall())

    def get_polys_offset(self, offset):
        self.c.execute(self.qstringoff, { 'offset': offset })
        return self.proc_polys(self.c.fetchall())

    def get_polys_america(self, code):
        self.c.execute(self.qstringamerica, { 'zone': "%America%", 'code' : code })
        return self.proc_polys(self.c.fetchall())

    def destroy(self):
        self.conn.close()
