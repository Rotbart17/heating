import time
import sqlite3
from sqlite3 import Error, Connection
import logging
import threading
import settings
from settings import SensorList
from table import Tables
import random
from multiprocessing import Queue
from queue import Empty


# Definitionen der Sensorklasse
# schaun wir mal was ich schon gelernt habe
# -------------------------------------------------------------------------------------------
class sensor(Tables):

    # connection zur DB
    conn : Connection
        
    # Zeit bis zur nächsten Abfrage eines Sensors in sec
    waittime = 10

    # Thread zu Messung anhalten
    threadstop : bool = False
    
    # Thread Merk Variable, damit man den Thread später wieder anhalten kann

    # DB Tabelle anlegen wenn notwendig
    # def __init__(self,tablename): 
    def __init__(self, tablename:str, sql_columns:str, queue_to_backend:Queue, queue_from_backend:Queue) -> None:
        super().__init__(tablename, sql_columns, queue_to_backend,queue_from_backend)
        self._create_table()


        # so, die Tabelle existiert, jetzt noch die Sensorliste aufbauen
        settings.SensorList.append(self)
        logging.info('Sensor '+ self.tablename +' in die Sensorliste eingehängt!')
        # ok jetzt ist eigetlich alles vorbereitet, jetzt noch die Sensorabfrage starten
        self.startthread()


    # DB Verbindung schließen wenn Objekt gelöscht wird
    def __del__(self):
        logging.debug(f'Sensor {self.tablename} stoppen')
        self.threadstop = True
        # wait for Thread to end
        self.conn.close()
        self.x.join()
        logging.info("Sensorobjekt " + self.tablename + " gelöscht.")
        

    def startthread(self):
        self.x = threading.Thread(target=self.sensor_envlope, name="Thread-"+self.tablename)
        logging.info('Starte Sensorabfrage '+ self.tablename + '!')
        settings.ThreadList.append(self.x)
        self.x.start()
        self._putqueuevalue()
        logging.debug('Sensorabfrage '+ self.tablename + ' gestartet!')
        
    # Das hier ist der Teil, der im Thread läuft
    def sensor_envlope(self):
        tn=self.tablename
        # einstweilen Mal Dummywerte zurückgeben bis ich die echten Funktionen habe
        # die die Sensoren abfragen
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
        def storevalue(temperature):
            maxtry=10
            t=0
            conn = sqlite3.connect(settings.DBPATH)
            sql = f"INSERT INTO {tn} (value, begin_date) VALUES ( {temperature}, datetime('now','localtime') );"
            while True:
                try:
                    cursor=conn.cursor()
                    cursor.execute("BEGIN")
                    conn.execute(sql)
                    cursor.execute("COMMIT")
                    # conn.commit()
                    logging.debug('Sensorwert in '+tn+' gespeichert!')
                    break
                except Exception as e:
                    logging.debug('DB-Fehler '+str(e)+' beim Schreiben in '+tn+' aufgetreten!')
                    t+=1
                    if t>=10:
                       logging.error('DB-Fehler '+str(e)+' beim Schreiben in '+tn+' 10 Mal aufgetreten! Breche ab')
                       exit(1) 
                    time.sleep(random.random())
                    continue
            conn.close()

        # Die Daten Wandeln und speichern
        def processvalue(name:str):
            
            while (self.threadstop == False):
                rawtemp = getvalue(name)
                temperature = convertvalue(rawtemp)
                storevalue(temperature)
                logging.debug('Sensorabfrage '+ name +' ist erfolgt!')
                time.sleep(self.waittime)
                self._getqueuevalue()
            logging.info('Sensorabfrage '+ name +' ist jetzt beendet!')

        # Warten, dass Thread wieder zurückkommt.
        processvalue(self.tablename)
        

        
        
