#!/usr/bin/env python3
# in diesem Modul wird die Datenaustauschstruktur für die Zeitsteuerung definiert
# sie versteckt die Datenbankzugriffe in einer Klasse


import settings
from dataclasses import dataclass
import logging
import sqlite3
from enum import Enum
from time import time

logging.basicConfig(
    filename='gui.log',
    filemode='w',
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.ERROR
)

@dataclass
class ZeitView:
    # Ein Feld von Tupeln die die gesamte Info der Zeitsteuerungsinfo beinhaltet
    Zeitsteuerungszeilen=[]
    

    # liest alle Daten der Zeitsteuerungstabelle
    def _zeitsteuerungload(self):
        try:
            with sqlite3.connect(settings.DBPATH) as db:
                logging.debug('Zeitsteuerungstabelle lesen!')
                cursor=db.cursor()
                sql= settings.sql_readzeitsteuerung
                cursor.execute(sql)
                self.Zeitsteuerungszeilen=cursor.fetchall()
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
            # jetzt den Inhalt der Tabelle wieder in die DB schreiben 
            sql= settings.sql_writezeitsteuerung
            # Speicherzeit zum Vermerk damit man weiß ob man alles lesen muss.
            changetime=time.time_ns()
            for i in value:
                i[6]=changetime
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
        return (self.Zeitsteuerungszeilen)

    @vZeitsteuerung.setter
    def vZeitsteuerung(self,value):
        self._zeitsteuerungwrite(value)
    
