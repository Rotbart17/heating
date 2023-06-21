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
    # Zeit bis zur nächsten Abfrage eines Sensors in sec
    waittime = 300

    # Wert des Sensors
    rawtemp = None

    # Temperatur in Grad
    temperature = None

    # Thread zu Messung anhalten
    threadstop = False

    # Tabelle die hier bearbeitet wird
    tn = None
    
    # Thread Merk Variable
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
            sensor.conn = sqlite3.connect(settings.DBPATH)
            logging.info('DB-Verbindung geöffnet')
        except Error as e:
            logging.error('Es konnte keine Verbindung zu Datenbank erstellt werden. Programm wird beendet')
            exit(1)
        try:
            c = sensor.conn.cursor()
            create_table_sql = sql_create_sensor_table_p1 + self.tn + sql_create_sensor_table_p2
            c.execute(create_table_sql)
            logging.info('Tabelle' + self.tn +' erstellt')
        except Error as e:
            logging.error('Es konnte kein Cursor in der Datenbank erstellt werden um die Tabellen zu erzeugen. Programm wird beendet!')
            exit(1)
        # so, die Tabelle existiert, jetzt noch die Sensorliste aufbauen
        # bsp: for f in SensorList:
        #          f.DoSomething()
        settings.SensorList.append(self)
        logging.info('Sensor '+self.tn+' in die Sensorliste eingehängt!')
        # ok jetzt ist eigetlich alles vorbereitet, jetzt noch die Sensorabfrage starten
        sensor.startthread(c)


    # DB Verbindung schließen wenn Objekt gelöscht wird
    def __del__(self):
        sensor.threadstop = True
        # wait for Thread to end
        sensor.x.join()
        sensor.conn.close()
        logging.info('fSensorobjekt '+self.tn+'gelöscht')
        

    # DB Tabelle leeren
    def cleanup(self,conn,tablename):
        c = conn.cursor()
        c.execute('DELETE FROM '+ tablename +';')
        c.commit()
        print('We have deleted', c.rowcount, 'records from '+ tablename + '!')
        conn.close()
        logging.warning('fSensortabelle '+tablename+' gelehrt')


    # DB Tabelle löschen
    def delete(self,conn,tablename):     
        c = conn.cursor()
        c.execute('DROP TABLE '+ tablename)
        conn.commit()
        conn.close()
        logging.warning('fSensortabelle '+tablename+' gelöscht')


    # hier muss die spezielle Abfrage für den Sensor bei der Vererbung eingesetzt werden
    def getvalue(self):
        pass
        # Abfrage
        # return (self.rawtemp)
        


    # Wert in Temperatur wandeln
    def convertvalue(self,rawtemp):
        self.rawtemp = rawtemp
        pass
        

    # Wert in DB speichern 
    def storevalue(self,temperature,conn):
        dt = datetime.datetime.now()
        sql = "INSERT INTO " + self.tn + " (value, begin_date) VALUES(" + temperature + " , " + dt + "); " 
        conn.execute(sql)
        self.conn.commit()
        logging.debug('fSensorwert in '+self.tn+' gespeichert!')
    

    # Die Daten Wandeln und speichern
    def processvalue(self,conn):
        while (not sensor.threadstop):
            self.rawtemp = sensor.getvalue()
            self.temperature = sensor.convertvalue(self.rawtemp)
            sensor.storevalue(self.temperature,conn)
            time.sleep(sensor.waittime)
        # Wenn Ende dann abbrechen
        # Warten, dass Thread wieder zurückkommt.



    # Messthread starten    
    def startthread(self,conn):
        global threads
        x = threading.Thread(target=sensor.processvalue, args=(conn,))
        threads.append(self.x)
        x.start()


# Klasse Kesselsensor anlegen 
class kesselsensor(sensor):
    tablename = "Kesselsensor"
    def __init__(self, tablename):
        super().__init__(tablename)
        return


    # Deconstructor wenn instanz gelöscht wird.
    def __del__(self):
        logging.debug('fSensor '+self.tn+'stoppen')
        return super().__del__()
        

    # hier muss die spezielle Abfrage für den Sensor bei der Vererbung eingesetzt werden
    def getvalue(self) -> float:
        
        if settings.V_Mode == True:
            return(2,38)  #entspricht 25Grad
        else:
        #  Abfrage
            logging.debug('Sensorwert '+self.tn+'abfragen')
        return (self.rawtemp)
        


    # Wert in Temperatur wandeln
    def convertvalue(self, rt) -> float:
        # umrechnung für den Kesselsensor 
        self.rt = rt
        temp = (-7,79670769172508*pow(rt,3))+(39,9983314997706*pow(rt,2))+(-109,299890516815*rt)+163,716704847826
        logging.debug('Sensorwert '+self.tn+'wandeln')
        return (temp)

