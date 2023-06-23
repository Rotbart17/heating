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
    waittime = 30

    # Wert des Sensors
    rawtemp : float
    rawtemp = 0.0

    # Temperatur in Grad
    temperature: float
    temperature = 0.0

    # Thread zu Messung anhalten
    threadstop = False

    # Sensortabelle die hier bearbeitet wird
    tn : str
    tn = ""
    
    # Thread Merk Variable, damit man den Thread später wieder anhalten kann
    # x 


    # DB Tabelle anlegen wenn notwendig
    def __init__(self,tablename): 
        # create a table from the create_table_sql statement
        # :param conn: Connection object
        # :param create_table_sql: a CREATE TABLE statement
        # :return:
        sql_create_sensor_table_p1 = "CREATE TABLE IF NOT EXISTS " 
        sql_create_sensor_table_p2 = " (id integer PRIMARY KEY AUTOINCREMENT NOT NULL,  \
                                        value real,              \
                                        begin_date text,         \
                                        end_date text,           \
                                        error integer            \
                                    ); "
        self.tn = tablename
                     
        try:
            self.conn = sqlite3.connect(settings.DBPATH)
            logging.info('DB-Verbindung geöffnet')
            
        except Error as e:
            logging.error('Es konnte keine Verbindung zu Datenbank erstellt werden. Programm wird beendet')
            exit(1)
        try:
            c = self.conn.cursor()
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
        logging.info('Sensor '+ self.tn +' in die Sensorliste eingehängt!')
        # ok jetzt ist eigetlich alles vorbereitet, jetzt noch die Sensorabfrage starten
        self.startthread()


    # DB Verbindung schließen wenn Objekt gelöscht wird
    def __del__(self):
        self.threadstop = True
        # wait for Thread to end
        self.x.join()
        self.conn.close()
        logging.info("Sensorobjekt " + self.tn + " gelöscht.")
        

    # DB Tabelle leeren
    def cleanup(self,tablename):
        c = self.conn.cursor()
        c.execute('DELETE FROM '+ tablename +';')
        c.commit()
        print('We have deleted', c.rowcount, 'records from '+ tablename + '!')
        c.close()
        logging.warning('fSensortabelle '+tablename+' gelehrt')


    # DB Tabelle löschen
    def delete(self,conn,tablename):     
        c = conn.cursor()
        c.execute('DROP TABLE '+ tablename)
        conn.commit()
        conn.close()
        logging.warning('fSensortabelle '+tablename+' gelöscht')


    # hier muss die spezielle Abfrage für den Sensor bei der Vererbung eingesetzt werden
    def getvalue(self) -> float:
        pass
        # Abfrage wird jeweils in der Unterklasse definiert, da sensorspezifisch
        return (self.rawtemp)
        


    # Wert in Temperatur wandeln, diese Klasse wird in der UNterklasse ersetzt
    def convertvalue(self) ->float: 
        # Abfrage wird jeweils in der Unterklasse definiert, da sensorspezifisch
        # self.temperature = 1.1 
        pass
        return (self.temperature)

      

    # Wert in DB speichern 
    def storevalue(self,temperature,conn):
        dt = datetime.datetime.now()
        sql = "INSERT INTO " + self.tn + " (value, begin_date) VALUES(" + temperature + " , " + dt + "); " 
        conn.execute(sql)
        conn.commit()
        logging.debug('fSensorwert in {self.tn} gespeichert!')
    

    # Die Daten Wandeln und speichern
    def processvalue(self,name:str):
        while (sensor.threadstop != True):
            self.rawtemp = self.getvalue()
            self.temperature = self.convertvalue()
            self.storevalue(self.temperature,conn)
            logging.info('Sensorabfrage '+ name +' erfolgt!')
            time.sleep(sensor.waittime)
        # Wenn Ende dann abbrechen
        # Warten, dass Thread wieder zurückkommt.



    # Messthread starten    
    def startthread(self):
        global threads
        self.x = threading.Thread(target=sensor.processvalue, args=(self.tn,))
        logging.info('Starte Sensorabfrage '+ self.tn + '!')
        self.x.start()


# Klasse Kesselsensor anlegen 
class kesselsensor(sensor):
    def __init__(self, tablename):
        self.tn = tablename
        super().__init__(self.tn)
        return


    # Deconstructor wenn instanz gelöscht wird.
    def __del__(self):
        logging.debug('fSensor {self.tn} stoppen')
        return super().__del__()
        

    # hier muss die spezielle Abfrage für den Sensor bei der Vererbung eingesetzt werden
    def getvalue(self) -> float:
        
        if settings.V_Mode == True:
            return(2.38)  #entspricht 25Grad
        else:
        #  Abfrage
            logging.debug('Sensorwert '+self.tn+'abfragen')
        return (self.rawtemp)
        


    # Wert in Temperatur wandeln
    def convertvalue(self) -> float:
        # umrechnung für den Kesselsensor 
        rt = self.rawtemp
        temp = (-7.79670769172508*pow(rt,3)) + (39.9983314997706*pow(rt,2)) + (-109.299890516815*rt) + 163.716704847826
        logging.debug('Sensorwert {self.tn} wandeln')
        return (temp)

