
import sqlite3
from sqlite3 import Error
import logging
import settings
from settings import SensorList, DBPATH, tablename
import os

# hier sind alle DB Przeduren gebündelt, die nicht in Classen definert sind.

# create SQlite DB 
def create_db(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        logging.info('fDB Version '+sqlite3.version+' erstellt')
    except Error as e:
        logging.error('fDie Datenbank konnte nicht erstellt werden')
        exit(1)
    finally:
        if conn:
            return (conn)


# open a database connection to a SQLite database
def open_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        logging.error('fDie Datenbank konnte nicht geöffnet werden')
        exit(1)
    finally:
        if conn:
            logging.info('fDatenbank geöffnet!')
            return (conn)

# Datenbankverbindung Schließen
def close_connection(conn):
    if conn:
        conn.close()
        return(True)


# hier werden nur Senostabellen angelegt
def create_sensor_table(conn,tablename):
    sql_create_sensor_table_p1 = " CREATE TABLE IF NOT EXISTS" 
    sql_create_sensor_table_p2 = " (         id integer PRIMARY KEY, \
                                            value real,              \
                                            begin_date text,         \
                                            end_date text,           \
                                            error integer,           \
                                            burner_on integer        \
                                        ); "
    create_table(conn, tablename, sql_create_sensor_table_p1,sql_create_sensor_table_p2)



# Tabelle anlegen wenn sie noch nicht existiert
def create_table(conn, tablename, sql_create_table_p1, sql_create_table_p2):
   
    try:
        c = conn.cursor()
        cts = sql_create_table_p1 + tablename + sql_create_table_p2
        c.execute(cts)
    except Error as e:
        logging.error('fTabelle '+tablename+' konnte nicht erstellt werden! Programm wird beendet')
        exit(1)
    finally:
        logging.info('fTabelle: '+tablename+' erstellt')
        return(True)
    
    
# Tabelle mit inhalt löschen
def drop_table(conn,tablename):
    cursor= conn.cursor()
    t = "DROP TABLE "+ tablename
    try:
        cursor.execute(t)
    except Error as e:
        logging.error('fTabelle '+tablename+' konte nicht gelöscht werden.')
        exit(1)
    finally:
        logging.info('fTabelle '+tablename+' gelöscht.')
        return(True)


# Tabelleninhalt löschen
def empty_table(conn, tablename):
    cursor= conn.cursor()
    t = "DELETE FROM "+ tablename
    try:
        cursor.execute(t)
    except Error as e:
        logging.error('fDaten in '+tablename+' konten nicht gelöscht werden.')
        exit(1)
    finally:
        logging.info('fDaten in '+tablename+' gelöscht.')
        return(True)

# Tabelle mit inhalt löschen
def drop_db(conn):
    close_connection(conn)
    try:
        os.remove(settings.DBPATH)
    except OSError:
        logging.info('fDatenbank konnte nicht gelöscht werden.')
        return (False)
    finally:
        logging.info('fDatenbank gelöscht.')
        return(True)


# Datenbank und "alle" Tabellen anlegen
def init_db_environment():
    # jetzt die Worktabelle definieren und initialisieren
    tn = settings.WorkDataView
 
    try:
        conn = sqlite3.connect(settings.DBPATH)
        logging.info('DB-Verbindung geöffnet')
        
    except Error as e:
        logging.error('Es konnte keine Verbindung zu Datenbank erstellt werden. Programm wird beendet')
        exit(1)
    try:
        c = conn.cursor()
        create_table_sql = settings.sql_create_view_table_p1 + tn + settings.sql_create_view_table_p2
        c.execute(create_table_sql)
        logging.info('Tabelle' + tn +' erstellt')
    except Error as e:
        logging.error('Es konnte kein Cursor in der Datenbank erstellt werden um die Tabellen zu erzeugen. Programm wird beendet!')
        exit(1)
    # so nun mal ein paar Init-datenschreiben und wenn noch nicht da die erste 
    # und einzige Zeile dieser Tabelle erzeugen

    sql = f"INSERT or REPLACE into {tn} (\
                            id, Winter, Kessel, Brauchwasser, Innen, Aussen, Pumpe_oben_an,  \
                            Pumpe_unten_an, Pumpe_Brauchwasser_an, Brenner_an, \
                            Brenner_Stoerung, Hand_Dusche ) \
                            values( 1, \
                            \"{settings.Winter}\",{settings.Kessel},{settings.Brauchwasser}, \
                              {settings.Innen},   {settings.Aussen}, \"{settings.Pumpe_oben_an}\",\
                            \"{settings.Pumpe_unten_an}\", \"{settings.Pumpe_Brauchwasser_an}\", \
                            \"{settings.Brenner_an}\",     \"{settings.Brenner_Stoerung}\",\
                            \"{settings.Hand_Dusche}\" \
                            );"

    c.execute(sql)
    conn.commit()
    conn.close()


    # so, die Tabelle existiert. Initdaten sind reingeschrieben.
    # weitere Tabellen, die naoch benötigt werden
    # Anzeigetabelle
    # Parametertabelle?

