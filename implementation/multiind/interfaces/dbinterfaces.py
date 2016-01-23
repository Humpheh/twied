import sqlite3
import ast


def proc_polystr(polys, weight):
    if len(polys) == 0:
        return []

    all_polys = []
    for i in polys:
        ji = ast.literal_eval(i[0])
        for p in ji['coordinates']:
            if isinstance(p[0], list):
                for x in p:
                    all_polys.append((x, weight))
            else:
                all_polys.append((p, weight))

    return all_polys


class GADMPolyInterface:
    def __init__(self, dbloc):
        self.conn = sqlite3.connect(dbloc)
        self.c = self.conn.cursor()
        orstr = " or ".join(['n{0} = :n{0}'.format(i) for i in range(1, 6)])
        self.qstring = "SELECT poly FROM gadm WHERE " + orstr

    def get_polys(self, name, weight):
        self.c.execute(self.qstring, {
            'n1': name, 'n2': name, 'n3': name, 'n4': name, 'n5': name,
        })

        polys = self.c.fetchall()
        return proc_polystr(polys, weight)

    def destroy(self):
        self.conn.close()


class CountryPolyInterface:
    def __init__(self, dbloc):
        self.conn = sqlite3.connect(dbloc)
        self.c = self.conn.cursor()
        self.qstring = "SELECT poly FROM countries WHERE name LIKE :name"

    def get_polys(self, name, weight):
        self.c.execute(self.qstring, {'name': name})

        polys = self.c.fetchall()
        return proc_polystr(polys, weight)

    def destroy(self):
        self.conn.close()


class TZPolyInterface:
    def __init__(self, dbloc):
        self.conn = sqlite3.connect(dbloc)
        self.c = self.conn.cursor()
        self.qstring = "SELECT poly FROM tz WHERE zone LIKE :zone"
        self.qstringoff = "SELECT poly FROM tz WHERE offset LIKE :offset"
        self.qstringamerica = "SELECT poly FROM tz WHERE zone LIKE :zone AND code = :code"

    def get_polys(self, name, weight):
        self.c.execute(self.qstring, {'zone': "%" + name + "%"})
        return proc_polystr(self.c.fetchall(), weight)

    def get_polys_offset(self, offset, weight):
        self.c.execute(self.qstringoff, {'offset': offset})
        return proc_polystr(self.c.fetchall(), weight)

    def get_polys_america(self, code, weight):
        self.c.execute(self.qstringamerica, {'zone': "%America%", 'code': code})
        return proc_polystr(self.c.fetchall(), weight)

    def destroy(self):
        self.conn.close()
