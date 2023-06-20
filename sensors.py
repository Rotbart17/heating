import time
import sqlite3
from sqlite3 import Error
import sys
import logging
import threading
import datetime
import settings
from settings import SensorList, DBPATH

# Definitionen der Sensorklasse
# schaun wir mal was ich schon gelernt habe

class sensor:

    # connection zur DB
    conn = None
    # Zeit bis zur nächsten Abfrage des Sensors in sec
    waittime = 300

    # Wert des Sensors
    rawtemp = None

    # Temperatur in Grad
    temperature = None

    # Thread zu Messung anhalten
    threadstop = False

    # Tabelle die hier bearbeitet wird
    tn = None
    
    # Threadlist
    threads = list()
    # Thread variable
    x = None


    # DB Tabelle anlegen wenn notwendig
    def __init__(self,tablename): 
        # create a table from the create_table_sql statement
        # :param conn: Connection object
        # :param create_table_sql: a CREATE TABLE statement
        # :return:
        sql_create_sensor_table_p1 = " CREATE TABLE IF NOT EXISTS" 
        sql_create_sensor_table_p2 = " (    id integer PRIMARY KEY,  \
                                        value real,              \
                                        begin_date text,         \
                                        end_date text,           \
                                        error integer            \
                                    ); "

        self.tn = tablename
       
        try:
            self.conn = sqlite3.connect(settings.DBPATH)
            logging.info('fDB-Verbindung geöffnet')
        except Error as e:
            logging.error('fEs konnte keine Verbindung zu Datenbank erstellt werden. Programm wird beendet')
            exit(1)
        try:
            c = self.conn.cursor()
            create_table_sql = sql_create_sensor_table_p1 + self.tn + sql_create_sensor_table_p2
            c.execute(create_table_sql)
            logging.info('fTabelle' + self.tn +' erstellt')
        except Error as e:
            logging.error('fEs konnte kein Cursor in der Datenbank erstellt werden um die Tabellen zu erzeugen. Programm wird beendet!')
            exit(1)
        # so, die Tabelle existiert, jetzt noch die Sensorliste aufbauen
        # bsp: for f in SensorList:
        #          f.DoSomething()
        settings.SensorList.append(self)
        logging.info('fSensor '+self.tn+' in die Sensorliste eingehängt!')
        # ok jetzt ist eigetlich alles vorbereitet, jetzt noch die Sensorabfrage starten
        self.startthread


    # DB Verbindung schließen wenn Objekt gelöscht wird
    def __del__(self):
        self.threadstop = True
        # wait for Thread end
        self.x.join()
        self.conn.close()
        logging.info('fSensorobjekt '+self.tn+'gelöscht')
        

    # DB Tabelle leeren
    def cleanup(self):
        c = self.conn.cursor()
        c.execute('DELETE FROM '+ self.tn +';')
        self.conn.commit()
        print('We have deleted', c.rowcount, 'records from '+ self.tn + '!')
        self.conn.close()
        logging.warning('fSensortabelle '+self.tn+' gelehrt')


    # DB Tabelle löschen
    def delete(self):     
        c = self.conn.cursor()
        c.execute('DROP TABLE '+ self.tn)
        self.conn.commit()
        self.conn.close()
        logging.warning('fSensortabelle '+self.tn+' gelöscht')


    # hier muss die spezielle Abfrage für den Sensor bei der Vererbung eingesetzt werden
    def getvalue(self):
        pass
        # Abfrage
        # return (self.rawtemp)
        


    # Wert in Temperatur wandeln
    def convertvalue(self):
        pass
        

    # Wert in DB speichern 
    def storevalue(self):
        c = self.conn.cursor()
        dt = datetime.datetime.now()
        sql = "INSERT INTO " + self.tn + " (value, begin_date) VALUES(" + self.temperature + " , " + dt + "); " 
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()
        logging.debug('fSensorwert in '+self.tn+' gespeichert!')
    

    # Die Daten Wandeln und speichern
    def processvalue(self):
        while (not self.threadstop):
            self.rawtemp = self.getvalue()
            self.temperature = self.convertvalue()
            self.storevalue()
            time.sleep(self.waittime)
        # Wenn Ende dann abbrechen
        # Warten, dass Thread wieder zurückkommt.



    # Messthread starten    
    def startthread(self):
        self.x = threading.Thread(target=self.processvalue, args=(1,))
        self.threads.append(self.x)
        self.x.start()
        self.x.join


# Klasse Kesselsensor anlegen 
class kesselsensor(sensor):
    tablename = "Kesselsensor"
    def __init__(self, tablename):
        super().__init__(tablename)

    def __del__(self):
        logging.debug('fSensor '+self.tn+'stoppen')
        return super().__del__()
        

    # hier muss die spezielle Abfrage für den Sensor bei der Vererbung eingesetzt werden
    def getvalue(self):
        pass
        # Abfrage
        # return (self.rawtemp)
        logging.debug('fSensorwert '+self.tn+'abfragen')


    # Wert in Temperatur wandeln
    def convertvalue(self):
        pass
        logging.debug('fSensorwert '+self.tn+'wandeln')


