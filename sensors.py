import time
import sqlite3
from sqlite3 import Error, Connection
import logging
import threading
import settings
from table import Tables
from dbinit import connect_db
import random
from multiprocessing.synchronize import Event


# Definitionen der Sensorklasse
# schaun wir mal was ich schon gelernt habe
# -------------------------------------------------------------------------------------------
class sensor(Tables):

    # connection zur DB
    conn : Connection
        
    # Zeit bis zur nächsten Abfrage eines Sensors in sec
    waittime = 10

    # Thread der Sensorabfrage, wird von Backend zum Einsammeln verwendet
    thread : threading.Thread

    # DB Tabelle anlegen wenn notwendig
    # def __init__(self,tablename): 
    def __init__(self, tablename:str, sql_columns:str, stop_event:Event) -> None:
        super().__init__(tablename, sql_columns, stop_event)
        self._create_table()


        # die Tabelle existiert, jetzt die Sensorabfrage starten
        self.startthread()


    def startthread(self):
        self.thread = threading.Thread(target=self.sensor_envlope, name="Thread-"+self.tablename)
        logging.info('Starte Sensorabfrage '+ self.tablename + '!')
        self.thread.start()
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
            conn = connect_db()
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
                       conn.close()
                       raise RuntimeError(f'DB-Fehler beim Schreiben in {tn}') from e
                    time.sleep(random.random())
                    continue
            conn.close()

        # Die Daten Wandeln und speichern
        def processvalue(name:str):
            
            while not self.stop_event.is_set():
                rawtemp = getvalue(name)
                temperature = convertvalue(rawtemp)
                storevalue(temperature)
                logging.debug('Sensorabfrage '+ name +' ist erfolgt!')
                self.stop_event.wait(self.waittime)
            logging.info('Sensorabfrage '+ name +' ist jetzt beendet!')

        # Warten, dass Thread wieder zurückkommt.
        try:
            processvalue(self.tablename)
        except Exception:
            # ohne Sensorwerte darf das Backend nicht weiterlaufen: alles anhalten
            logging.exception('Sensorthread '+self.tablename+' ist abgebrochen, Backend wird gestoppt!')
            self.stop_event.set()
        

        
        
