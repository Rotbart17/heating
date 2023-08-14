
import sqlite3
from sqlite3 import Error
import logging
import settings
from settings import SensorList, DBPATH
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


# hier werden nur Sensortabellen angelegt
# def create_sensor_table(conn,tablename):
#     sql_create_sensor_table_p1 = " CREATE TABLE IF NOT EXISTS" 
#     sql_create_sensor_table_p2 = " (         id integer PRIMARY KEY, \
#                                            value real,              \
#                                            begin_date text,         \
#                                             end_date text,           \
#                                            error integer,           \
#                                            burner_on integer        \
#                                        ); "
#   create_table(tablename, sql_create_sensor_table_p1,sql_create_sensor_table_p2)



# Tabelle anlegen wenn sie noch nicht existiert
def create_table(tablename, sql_create_table_p1, sql_create_table_p2):

    try:
        conn = sqlite3.connect(settings.DBPATH)
        logging.info('DB-Verbindung geöffnet')
        
    except Error as e:
        logging.error('Es konnte keine Verbindung zu Datenbank erstellt werden. Programm wird beendet')
        exit(1)
    try:
        c = conn.cursor()
        create_table_sql = sql_create_table_p1 + tablename + sql_create_table_p2
        c.execute(create_table_sql)
        conn.close()
        logging.info('Tabelle' + tablename +' erstellt')
    except Error as e:
        logging.error('Es konnte kein Cursor in der Datenbank erstellt werden um die Tabellen zu erzeugen. Programm wird beendet!')
        exit(1)
    return

# Tabelle initialisieren
def init_table(tablename,init_sql, x:float | None=None, y: float |None=None ):
    try:
        conn = sqlite3.connect(settings.DBPATH)
        logging.info('DB-Verbindung geöffnet')
        
    except Error as e:
        logging.error('Es konnte keine Verbindung zur Datenbank erstellt werden. Programm wird beendet')
        exit(1)
    try:
        c = conn.cursor()
        c.execute(init_sql)
        conn.commit()
        conn.close()
        logging.info('Tabelle' + tablename + ' ' +str(x)+ ' ' + str(y)+ ' initialisiert')
    except Error as e:
        logging.error('Es konnte kein Cursor in der Datenbank erstellt werden um die Tabellen zu erzeugen. Programm wird beendet!')
        exit(1)
    return    

    
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



tempdict={}
def init_Kesselvalues(name):
    k=0
    tn= name
    # alles mal 10, damit man range() mit int verwenden kann.
    # die Kennlinie geht von -30 bis 30 Grad Schrit 0.5
    for i in range(-300,300,5):
        x= float(i/10)
        y=eval(settings.KesselKennlinie)
        tempdict[x]= y
        
        # die Daten müssen nun in die Datenbank
        sql = settings.sql_init_Kesselkennlinie
        init_table(tn,sql,x,y)





# Datenbank und "alle" Tabellen anlegen
def init_db_environment():
    
    # jetzt die Anzeigeworktabelle definieren und initialisieren
    tn = settings.WorkDataView
    create_table(tn,settings.sql_create_view_table_p1, settings.sql_create_view_table_p2 )
    
    # so nun mal ein paar Init-datenschreiben und wenn noch nicht da die erste 
    # und einzige Zeile dieser Tabelle erzeugen
 
    init_table(tn,settings.init_WorkDataView_sql)
    # so, die Tabelle existiert. Initdaten sind reingeschrieben.

    # nun die die Tabelle für die Kesselkennlinie erzeugen und dann mit initialen 
    # Werten füllen
    tn= settings.KesselSollTemperatur
    create_table(tn, settings.sql_kennlinie_p1,settings.sql_kennlinie_p2)
    init_Kesselvalues(tn)

    # Zeitsteuertabelle (Brauchwasser, Heizen , Nachtabsenkung, von, bis)
    tn= settings.ZeitSteuerung
    create_table(tn,settings.sql_zeitsteuerung_p1,settings.sql_zeitsteuerung_p2)
    # hier kein Init! Die ersten Daten kommen über die GUI.



    
    # weitere Tabellen, die noch benötigt werden
    # Parametertabelle?

# was brauchen wir denn alles an Tabellen:
# Brauchwassergrafik
# Kesselgrafik
# Innen-grafik
# Aussengrafik
# Kesselkennliniengrafik

# Wintertemp
# Brauchwassertemp 
# Loginfo
# löscht Fehlerstatus

