#!/usr/bin/env python3
# in diesem Modul wird die Datenaustauschstruktur für die Sensoren definiert
# sie versteckt die Datenbankzugriffe in einer Klasse
# so zumindest die Idee!

import settings
from dataclasses import dataclass, field
import logging
import sqlite3
import time
import threading
from enum import Enum


logging.basicConfig(
    filename='gui.log',
    filemode='w',
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.ERROR
)

class sens(Enum):
    Kesselsensor=0
    Aussensensor=1
    Innensensor=2
    Brauchwassersensor=3

##### Start der Idee mit der Idee  der Dataclass
@dataclass
class SensorView:

    # Liste für die Sensoren, eine für X-Werte, die andere für Y-Werte.
    _SensorXListe=[]
    _SensorYListe=[]
    
    # Listen für die Temperaturdaten der Sensoren. Nach x und ygetrennt wegen der Anzeige
    _KesselIstDaten_x : list = field(default_factory=list)
    _KesselIstDaten_y : list = field(default_factory=list)
    _BrauchwasserDaten_x : list = field(default_factory=list)
    _BrauchwasserDaten_y : list = field(default_factory=list)
    _InnenDaten_x : list = field(default_factory=list)
    _InnenDaten_y : list = field(default_factory=list)
    _AussenDaten_x : list = field(default_factory=list)
    _AussenDaten_y : list = field(default_factory=list)
    
        
    # Wartezeit in Sec bevor die nächste Abfrage der Sensordaten durchgeführt werden
    _sensorsleeptime : int = 60
    
    # dummy Definition wird dann in der Hauptlklasse gesetzt
    threadstop=False
    
    def __post_init__(self):
        # damit man die Sensoren in einer Schleife abfragen kann, müssen sie in eine Liste
        # Jason meinte man sollte ien Feld aus Pointern machen. Für C hat er recht.
        # aber so müsste es ja auchgehen.
        self._SensorXListe.append(self._KesselIstDaten_x)
        self._SensorXListe.append(self._AussenDaten_x)
        self._SensorXListe.append(self._InnenDaten_x)
        self._SensorXListe.append(self._BrauchwasserDaten_x)
        self._SensorYListe.append(self._KesselIstDaten_y)
        self._SensorYListe.append(self._AussenDaten_y)
        self._SensorYListe.append(self._InnenDaten_y)
        self._SensorYListe.append(self._BrauchwasserDaten_y)
        
        
        # Laden der initialen SensorWerte
        self._sensordataload()
        global sensor_poll
        _dummy=0 
        self.sensor_poll = threading.Thread(target=self._sensorpolling, name="Thread-GUI-Sensorpolling", args=(_dummy,))
        logging.info('Starte DB-Abfrage Sensor Thread!')
        settings.ThreadList.append(self.sensor_poll)
        self.sensor_poll.start()
        logging.debug('DB-Abfrage Thread Sensor gestartet!')
        
        

    # lädt die letzten Werte der Sensoren für die Anzeige
    def _sensordataload(self):
        try:
            with sqlite3.connect(settings.DBPATH) as db:
                cursor=db.cursor()
                # Hier kommt nun eine Schleife über alle Sensoren
                # die in jeder Sensortabelle, die Daten der letzten 24h abfragt
                # diese Datenmenge muss ggf. reduziert werden, da sonst zu viele Messwerte
                # für die Anzeige vorhanden sind. Die Ergebnisse müssen wieder der jeweiligen Liste 
                # zugeordnet werden. Dann kann die Anzeige sie hoffentlich verarbeiten.
                i=0
                for tn in settings.TemperaturSensorList:
                    xl=[]
                    yl=[]
                    sql = f"SELECT begin_date FROM {tn} WHERE begin_date >= datetime('now', '-24 hours');"
                    cursor.execute(sql)
                    results=cursor.fetchall()
                    # Der x-Wert ist die Zeit
                    xl = [item[0] for item in results]
                    self._SensorXListe[i] = xl

                    # Der y-Wert ist die Temperatur
                    sql = f"SELECT value FROM {tn} WHERE begin_date >= datetime('now', '-24 hours');"
                    cursor.execute(sql)
                    results=cursor.fetchall()
                    yl = [item[0] for item in results]
                    self._SensorYListe[i] = yl
                    i+=1
            cursor.close()
            db.close()
        except sqlite3.Error as e:
            logging.error(f"Error {e} ist aufgetreten")
            exit(1)

    # pollt regelmäßig neue Sensordaten für die Anzeige 1 mal pro Minute
    def _sensorpolling(self,dummy):
        while (self.threadstop ==False):
            self._sensordataload()
            logging.debug('Sensordata Pollen')
            time.sleep(self._sensorsleeptime)
            
   
   
    @property
    def vKesselIstDaten_x(self):
        return self._SensorXListe[sens.Kesselsensor.value]

    @property
    def vKesselIstDaten_y(self):
        return self._SensorYListe[sens.Kesselsensor.value]

    @property
    def vAussenDaten_x(self):
        return self._SensorXListe[sens.Aussensensor.value]

    @property
    def vAussenDaten_y(self):
        return self._SensorYListe[sens.Aussensensor.value]

    @property
    def vInnenDaten_x(self):
        return self._SensorXListe[sens.Innensensor.value]

    @property
    def vInnenDaten_y(self):
        return self._SensorYListe[sens.Innensensor.value]
       
    @property
    def vBrauchwasserDaten_x(self):
        return self._SensorXListe[sens.Brauchwassersensor.value]

    @property
    def vBrauchwasserDaten_y(self):
        return self._SensorYListe[sens.Brauchwassersensor.value]         
            
