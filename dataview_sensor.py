#!/usr/bin/env python3
# in diesem Modul wird die Datenaustauschstruktur für die Sensoren definiert
# sie versteckt die Datenbankzugriffe in einer Klasse
# so zumindest die Idee!

import settings
from dataclasses import dataclass
import logging
import sqlite3
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

    # Liste für die Sensoren
    _SensorXListe=[]
    _SensorYListe=[]

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

     
