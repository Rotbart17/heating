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
class ZeitView:
    # Ein Feld von Tupeln die die gesamte Info der Zeitsteuerungsinfo beinhaltet
    _Zeitsteuerung=[]

    # Daten der Zeitsteuerung laden
    def _zeitsteuerungload(self):
        try:
            with sqlite3.connect(settings.DBPATH) as db:
                logging.debug('Zeitsteuerung lesen!')
                cursor=db.cursor()
                sql= settings.sql_readzeitsteuerung
                cursor.execute(sql)
                t=cursor.fetchall()
                # self._Zeitsteuerung=[item[0] for item in t]
                cursor.close()
            db.close()
        except sqlite3.Error as e:
            logging.error(f"Der Fehler {e} ist beim Lesen der Zeitsteuerung aufgetreten")
            exit(1)

    def _zeitsteuerungwrite(self,value):
        try:
            db=sqlite3.connect(settings.DBPATH)
            logging.debug('Zeitsteuerungs Datensatz in DB schreiben!')
            cursor=db.cursor()
            sql= settings.sql_writezeitsteuerung
            cursor.execute(sql,value)
            db.commit()
            cursor.close()
            db.close()

        except sqlite3.Error as e:
            logging.error(f"Der Fehler {e} ist beim Schreiben der Kesselkennlinie_y aufgetreten")
            exit(1)

