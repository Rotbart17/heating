import time
import sqlite3
from sqlite3 import Error, Connection
import sys
import logging
import threading
import datetime
import settings
from settings import SensorList, DBPATH

# Definitionen der Sensorklasse
# schaun wir mal was ich schon gelernt habe
# -------------------------------------------------------------------------------------------
class sensor:

    # connection zur DB
    conn : Connection
        
    # Zeit bis zur nächsten Abfrage eines Sensors in sec
    waittime = 10

    # Thread zu Messung anhalten
    threadstop : bool = False

    # Sensortabelle die hier bearbeitet wird
    tn : str = ""
    
    # Thread Merk Variable, damit man den Thread später wieder anhalten kann
    # x 

    
    

    # DB Tabelle anlegen wenn notwendig
    def __init__(self,tablename): 
        
        self.tn = tablename
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
        logging.debug('fSensor {self.tn} stoppen')
        self.threadstop = True
        # wait for Thread to end
        self.x.join()
        sensor.conn.close()
        logging.info("Sensorobjekt " + self.tn + " gelöscht.")
        

    # DB Tabelle leeren
    def cleanup(self,tablename):
        c = sensor.conn.cursor()
        c.execute('DELETE FROM '+ tablename +';')
        sensor.conn.commit()
        print('We have deleted', c.rowcount, 'records from '+ tablename + '!')
        sensor.conn.close()
        logging.warning('Sensortabelle '+tablename+' gelehrt')


    # DB Tabelle löschen
    def delete(self,conn,tablename):     
        c = conn.cursor()
        c.execute('DROP TABLE '+ tablename)
        conn.commit()
        conn.close()
        logging.warning('Sensortabelle '+tablename+' gelöscht')


    def startthread(self):
        global threads
        self.x = threading.Thread(target=self.sensor_envlope, name="Thread-"+self.tn, args=(self.tn,))
        logging.info('Starte Sensorabfrage '+ self.tn + '!')
        settings.ThreadList.append(self.x)
        # self.x.setDaemon(True)
        self.x.start()
        logging.debug('Sensorabfrage '+ self.tn + ' gestartet!')
        
    def sensor_envlope(self,tablename):
      
        tn = tablename
        # einstweilen Mal Dummywerte zurückgeben bis ich die echten Funktionen habe
        def kessel(tn) -> float:
            pass
            return (settings.rawvaluedict[tn])

        def innen(tn) -> float:
            pass
            return (settings.rawvaluedict[tn])
    
        def aussen(tn) -> float:
            pass
            return (settings.rawvaluedict[tn])
        
        def brauchwasser(tn) -> float:
            pass
            return (settings.rawvaluedict[tn])

        # Dictionary für den Wertabfrage der Sensoren
        getfromspecificsensor = {
            "Kesselsensor" : kessel,
            "Aussensensor" : aussen,
            "Innensensor" : innen,
            "Brauchwassersensor" : brauchwasser
        }

        # hier muss die spezielle Abfrage für den Sensor bei der Vererbung eingesetzt werden
        def getvalue(name) -> float:
            tn = name
            if settings.V_Mode == True:
                rawtemp = settings.rawvaluedict[tn]()  #entspricht 25Grad
            else:
                rawtemp = getfromspecificsensor[tn](tn)
                logging.debug('Sensorwert '+tn+' abfragen')
            return (rawtemp)
        
        # Wert in Temperatur wandeln
        def convertvalue(rawtemp:float) -> float:
            # umrechnung für den Kesselsensor 
            rt = rawtemp
            temp = float(eval(settings.sensordict[tn]))
            logging.debug('Sensorwert '+tn+ ' '+ str(rt)+ '->'+ str(temp)+' wandeln')
            return (temp)
        
        # Wert in DB speichern 
        def storevalue(temperature,conn):
            dt = datetime.datetime.now()
            sql = "INSERT INTO " + tn + " (value, begin_date) VALUES(" + str(temperature) + " , \"" + str(dt) + "\"); " 
            conn.execute(sql)
            conn.commit()
            logging.debug('Sensorwert in '+tn+' gespeichert!')
            

    # Die Daten Wandeln und speichern
        def processvalue(name:str):
            conn = sqlite3.connect(settings.DBPATH)
            while (sensor.threadstop == False):
                rawtemp = getvalue(name)
                temperature = convertvalue(rawtemp)
                storevalue(temperature,conn)
                logging.debug('Sensorabfrage '+ name +' ist erfolgt!')
                time.sleep(sensor.waittime)
            # Wenn Ende dann abbrechen
            conn.close()
            logging.info('Sensorabfrage '+ name +' ist jetzt beendet!')
            # Warten, dass Thread wieder zurückkommt.
        processvalue(self.tn)

        
        
