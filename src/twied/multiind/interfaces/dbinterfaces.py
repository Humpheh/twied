import sqlite3
import ast


def proc_polystr(polys, weight):
    """
    Process a string of polygons into an array of polygons with
    a weight.

    :param polys: The string of the polygon data.
    :param weight: The weight of the polygons.
    :return: Array of tuples of (polygon, weight).
    """
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
    """
    Interface with the GADMPoly database table.
    """
    def __init__(self, dbloc):
        """
        Initialise the database interface.

        :param dbloc: The location of the sqlite3 database.
        """
        self.conn = sqlite3.connect(dbloc)
        self.c = self.conn.cursor()
        orstr = " or ".join(['n{0} = :n{0}'.format(i) for i in range(1, 6)])
        self.qstring = "SELECT poly FROM gadm WHERE " + orstr

    def get_polys(self, name, weight):
        """
        Gets the polygons for a name of a administrative district.

        :param name: The name of the area.
        :param weight: The weight of the returned polygons.
        :return: The array of polygons and weights.
        """
        self.c.execute(self.qstring, {
            'n1': name, 'n2': name, 'n3': name, 'n4': name, 'n5': name,
        })

        polys = self.c.fetchall()
        return proc_polystr(polys, weight)

    def destroy(self):
        """
        Close the connection.
        """
        self.conn.close()


class CountryPolyInterface:
    """
    Interface with the Country polygon database table.
    """
    def __init__(self, dbloc):
        """
        Initialise the database interface.

        :param dbloc: The location of the sqlite3 database.
        """
        self.conn = sqlite3.connect(dbloc)
        self.c = self.conn.cursor()
        self.qstring = "SELECT poly FROM countries WHERE name LIKE :name"

    def get_polys(self, name, weight):
        """
        Gets the polygons for a name of a Country.

        :param name: The name of the area.
        :param weight: The weight of the returned polygons.
        :return: The array of polygons and weights.
        """
        self.c.execute(self.qstring, {'name': name})

        polys = self.c.fetchall()
        return proc_polystr(polys, weight)

    def destroy(self):
        """
        Close the connection.
        """
        self.conn.close()


class TZPolyInterface:
    """
    Interface with the Timezone polygon database table.
    """
    def __init__(self, dbloc):
        """
        Initialise the database interface.

        :param dbloc: The location of the sqlite3 database.
        """
        self.conn = sqlite3.connect(dbloc)
        self.c = self.conn.cursor()
        self.qstring = "SELECT poly FROM tz WHERE zone LIKE :zone"
        self.qstringoff = "SELECT poly FROM tz WHERE offset LIKE :offset"
        self.qstringamerica = "SELECT poly FROM tz WHERE zone LIKE :zone AND code = :code"

    def get_polys(self, name, weight):
        """
        Gets the polygons for a timezone.

        :param name: The name of the area.
        :param weight: The weight of the returned polygons.
        :return: The array of polygons and weights.
        """
        self.c.execute(self.qstring, {'zone': "%" + name + "%"})
        return proc_polystr(self.c.fetchall(), weight)

    def get_polys_offset(self, offset, weight):
        """
        Gets the polygons for a timezone using the offset value.

        :param offset: The offset of the timezone.
        :param weight: The weight of the returned polygons.
        :return: The array of polygons and weights.
        """
        self.c.execute(self.qstringoff, {'offset': offset})
        return proc_polystr(self.c.fetchall(), weight)

    def get_polys_america(self, code, weight):
        """
        Gets the polygons for American timezones.

        :param code: The american code string.
        :param weight: The weight of the returned polygons.
        :return: The array of polygons and weights.
        """
        self.c.execute(self.qstringamerica, {'zone': "%America%", 'code': code})
        return proc_polystr(self.c.fetchall(), weight)

    def destroy(self):
        """
        Close the connection.
        """
        self.conn.close()
