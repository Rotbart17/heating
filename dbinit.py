
import sqlite3
from sqlite3 import Error

# Constanten
DBPATH = r"./heizung.db"
TABLELIST = ["Kesselsensor", "Aussensensor", "Innensensor", "Brauchwassersensor", "Brennersensor"]
sql_create_sensor_table_p1 = " CREATE TABLE IF NOT EXISTS" 
sql_create_sensor_table_p2 =" (         id integer PRIMARY KEY,  \
                                        value real,              \
                                        begin_date text,         \
                                        end_date text,           \
                                        error integer            \
                                    ); "


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            return (conn)
           #  conn.close()

def open_connection(db_file):
    """ open a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
        return(False)
    finally:
        if conn:
            conn.close()
            return (True)

# !!!
# Tabellen erzeugen wenn notwendig
    # Tabellenname als Liste
def create_table(conn, tablename,create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)




# Tabellen leeren
# Tabellen löschen
# DB löschen

# Eine DB erzeugen wenn notwendig
def db_open(DBPATH):
    conn = None
    if (open_connection(DBPATH) is False):
        conn = create_connection(DBPATH)
    else:
        for (i in TABLELIST):
            tablename=sql_create_sensor_table_p1 + i + sql_create_sensor_table_p2
            create_table(conn,tablename,create_table_sql)
