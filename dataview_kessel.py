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


@dataclass
class KesselView:
        # Laden der Kesselkennlinie mit x und y Werten
    def _kesseldataload(self):
        try:
            with sqlite3.connect(settings.DBPATH) as db:
                logging.debug('Kesselkennlinie lesen!')
                cursor=db.cursor()
                sql= f"SELECT value_x from {settings.KesselSollTemperatur} ;"
                cursor.execute(sql)
                t=cursor.fetchall()
                self._KesselDaten_x=[item[0] for item in t]
                sql= f"SELECT value_y from {settings.KesselSollTemperatur} ;"
                cursor.execute(sql)
                t=cursor.fetchall()
                cursor.close()
                self._KesselDaten_y=[item[0] for item in t]
            db.close()
        except sqlite3.Error as e:
            logging.error(f"Der Fehler {e} ist beim Lesen der Kesselkennlinie aufgetreten")
            exit(1)


    

    # Speichern der Kesselkennlinie
    # immer die ganze Kennlinie, wird nur beim Ändern der Daten aufgerufen.
    # aber eigentlich muss man die x-Anteile nie schreiben die sind ja fix.
    def _writeKesselDaten_x(self,value):
        self._KesselDaten_x=value.copy()
        try:
            with sqlite3.connect(settings.DBPATH) as db:
                logging.debug('Kesselkennline in DB schreiben!')
                cursor=db.cursor()
                sql= settings.sql_write_KesselKennlinie_x
                i=1
                for _ in range(int(settings.AussenMinTemp),int(settings.AussenMaxTemp),int(settings.AussenTempStep)):
                    t=(self._KesselDaten_x[i-1],i)
                    cursor.execute(sql,t)
                    i+=1
                cursor.close()
            db.close()
        except sqlite3.Error as e:
            logging.error(f"Der Fehler {e} ist beim Schreiben der Kesselkennlinie_x aufgetreten")
            exit(1)
          

    def _writeKesselDaten_y(self,value):
        self._KesselDaten_y=value.copy()
        try:
            db=sqlite3.connect(settings.DBPATH)
            logging.debug('Kesselkennline in DB schreiben!')
            cursor=db.cursor()
            sql= settings.sql_write_KesselKennlinie_y
            i=1
            for _ in range(int(settings.AussenMinTemp*10),int(settings.AussenMaxTemp*10),int(settings.AussenTempStep*10)):
                t=(self._KesselDaten_y[i-1],i)
                cursor.execute(sql,t)
                i+=1
            db.commit()
            cursor.close()
            db.close()

        except sqlite3.Error as e:
            logging.error(f"Der Fehler {e} ist beim Schreiben der Kesselkennlinie_y aufgetreten")
            exit(1)
