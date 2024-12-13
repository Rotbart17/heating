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
    _Zeitsteuerungszeilen=[]
    

    # liest alle Daten der Zeitsteuerungstabelle
    def _zeitsteuerungload(self):
        try:
            with sqlite3.connect(settings.DBPATH) as db:
                logging.debug('Zeitsteuerungstabelle lesen!')
                cursor=db.cursor()
                sql= settings.sql_readzeitsteuerung
                cursor.execute(sql)
                self._Zeitsteuerungszeilen=cursor.fetchall()
                # self._Zeitsteuerungszeilen=[item for item in t]
                cursor.close()
            db.close()
        except sqlite3.Error as e:
            logging.error(f"Der Fehler {e} ist beim Lesen der Zeitsteuerung aufgetreten")
            exit(1)

    # schreibt eine Zeile in die Zeitteuerungstabelle
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

