import enum
import sqlite3


class CombinationModifier(enum.Enum):
    And = "And"
    Or = "Or"
    Xor = "Xor"

    def __str__(self):
        return str(self.value)




def execute_read(database, query):
    con = sqlite3.connect(database)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    con.close()
    return rows


def execute_write(database, query):
    con = sqlite3.connect(database)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(query)
    con.commit()
    con.close()


def get_all(database, table):
    query = "Select * from " + table
    return execute_read(database, query)


def insert(database, table, **kwargs):
    num_items = len(kwargs)
    count = 0
    keys = " ("
    vals = " ("
    for key, val in kwargs.items():
        keys += "'" + key + "'"
        vals += "'" + val + "'"
        if count < num_items - 1:
            keys += ", "
            vals += ", "
        count += 1
    keys += ") "
    vals += ") "
    query = "Insert Into " + table + keys + "VALUES" + vals

    execute_write(database, query)


def get_all_with_constraint(database, table, modifier=CombinationModifier.And, **kwargs):
    num_items = len(kwargs)
    count = 0
    q = " "
    for key, val in kwargs.items():
        q += str(key) + "='" + str(val) + "'"
        if count < num_items - 1:
            q += " " + str(modifier) + " "
        count += 1
    query = "Select * From " + table + " Where" + q

    con = sqlite3.connect(database)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    con.close()
    return rows
