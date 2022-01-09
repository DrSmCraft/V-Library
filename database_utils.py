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
    query = "SELECT * FROM " + table
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
    query = "INSERT INTO " + table + keys + "VALUES" + vals

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
    query = "SELECT * FROM " + table + " WHERE" + q

    con = sqlite3.connect(database)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    con.close()
    return rows


def set_attr_with_constraint(database, table, constraint_attr, modifier=CombinationModifier.And, **kwargs):
    num_items = len(kwargs)
    count = 0
    q = " "
    constraints = {}
    for key, val in kwargs.items():
        if key not in constraint_attr:
            q += str(key) + "='" + str(val) + "'"
            if count < num_items - 1:
                q += ", "
        else:
            constraints[key] = val

        count += 1
    c = ""
    for key, val in constraints.items():
        c += str(key) + "='" + str(val) + "'"
        if count < len(constraints) - 1:
            q += " " + str(modifier) + " "
        count += 1

    query = "UPDATE " + table + " SET " + q + " WHERE " + c
    query = query.replace(",  WHERE", " WHERE").replace("  ", " ")
    print(query)
    con = sqlite3.connect(database)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    result = cur.execute(query)
    con.commit()
    con.close()
    print(result)


