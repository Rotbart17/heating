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

    # schreibt die Liste der Dictionaryzeilen in die Zeitteuerungstabelle
    def _zeitsteuerungwrite(self,value):
        try:
            db=sqlite3.connect(settings.DBPATH)
            logging.debug('Zeitsteuerungs Datensätze in DB schreiben!')
            cursor=db.cursor()
            cursor.execute("BEGIN")
            # Tabelleninhalt löschen
            sql= settings.sql_deletezeitsteuerung
            cursor.execute(sql)
            # jetzt den Inhalt der Tabelle wiedr in die DB schreiben 
            sql= settings.sql_writezeitsteuerung
            for i in value:
                cursor.execute(sql,i)
            cursor.execute("COMMIT")
            cursor.close()
        
        except sqlite3.Error as e:
            cursor.execute("ROLLBACK")
            logging.error(f"Der Fehler {e} ist beim Schreiben der Zeitsteuerungstabelle aufgetreten")
            exit(1)
        finally:
            db.close()
    
    @property
    def vZeitsteuerung(self):
        return (self._Zeitsteuerungszeilen)

    @vZeitsteuerung.setter
    def vZeitsteuerung(self,value):
        self._zeitsteuerungwrite(value)
    
