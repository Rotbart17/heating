
import sqlite3
from sqlite3 import Error
import logging
import settings
from settings import DBPATH


# create SQlite DB 
def create_db(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        logging.info(f'DB Version {sqlite3.version} erstellt')
        conn.close()
    except Error as e:
        logging.error(f'Die Datenbank konnte nicht erstellt werden! Fehler:{e}')
        exit(1)
    

# open a database connection to a SQLite database
def open_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        logging.error(f'Die Datenbank konnte nicht geöffnet werden! Fehler:{e}')
        exit(1)
    finally:
        if conn:
            logging.info('Datenbank geöffnet!')
            return (conn)

# Datenbankverbindung Schließen
def close_connection(conn):
    if conn:
        conn.close()
        return(True)


def checktable(tablename):
    erg=False    
    t=0
    try:
        conn = sqlite3.connect(DBPATH)
        logging.info('DB-Verbindung geöffnet')
        
    except Error as e:
        logging.error('Es konnte keine Verbindung zur Datenbank erstellt werden. Programm wird beendet')
        exit(1)
    try:
        c = conn.cursor()
        # t=c.execute(f"SELECT COUNT(*) FROM {tablename}").fetchone()[0]
        t= c.execute(f"SELECT EXISTS(SELECT name FROM sqlite_master WHERE type='table' AND name = '{tablename}');").fetchone()[0]
        conn.close()
        logging.info(f'Tabelle {tablename} enthält: {str(t)} Datensätze')
        if t>0 :
            erg=True
        else:
            erg=False
    except Error as e:
        logging.info(f'Es konnte die Tabelle {tablename} nicht abgefragt werden! Fehler: {e}')
    
    return (erg)    
    

# Datenbank und "alle" Tabellen anlegen
def init_db_environment():
    create_db(settings.DBPATH)
 
   
   
# noch offene Punkte ZZ
# Loginfo
# löscht Fehlerstatus


