#!/usr/bin/env python3
# in diesem Modul wird die Datenaustauschstruktur für die Zeitsteuerung definiert
# sie versteckt die Datenbankzugriffe in einer Klasse


import settings
from dataclasses import dataclass, field
import logging 
import sqlite3
from enum import Enum
import time
from time import time,time_ns


logging.basicConfig(
    filename='gui.log',
    filemode='w',
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.ERROR
)

@dataclass
class ZeitView:
    # Ein Feld, das die gesamte Info der Zeitsteuerung beinhaltet.
    # Durch default_factory wird sichergestellt, dass jede Instanz eine eigene Liste bekommt.
    Zeitsteuerungszeilen: list = field(default_factory=list)
    

    # liest alle Daten der Zeitsteuerungstabelle
    def _zeitsteuerungload(self):
        try:
            # Die 'with'-Anweisung kümmert sich um das Öffnen und Schließen der Verbindung.
            with sqlite3.connect(settings.DBPATH) as db:
                logging.debug('Zeitsteuerungstabelle lesen!')
                cursor=db.cursor()
                sql= settings.sql_readzeitsteuerung
                cursor.execute(sql)
                self.Zeitsteuerungszeilen=cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Der Fehler {e} ist beim Lesen der Zeitsteuerung aufgetreten")
            exit(1)

    # schreibt die Liste der Dictionaryzeilen in die Zeitteuerungstabelle
    def _zeitsteuerungwrite(self, value: list[dict]):
        """
        Schreibt die komplette Zeitsteuerungstabelle atomar neu.
        Erst wird alles gelöscht, dann die neuen Werte eingefügt.
        """
        changetime = time_ns()
        
        # Erstelle eine Kopie der Daten und setze den aktuellen Zeitstempel.
        # 'value' ist eine Liste von Dictionaries aus der GUI.
        data_to_write = []
        for row in value:
            new_row = row.copy()
            new_row['changetime'] = changetime
            data_to_write.append(new_row)

        try:
            # Die 'with'-Anweisung stellt eine transaktionale Operation sicher.
            with sqlite3.connect(settings.DBPATH) as db:
                cursor = db.cursor()
                logging.debug('Zeitsteuerungs Datensätze in DB schreiben!')
                
                # 1. Tabelleninhalt löschen
                cursor.execute(settings.sql_deletezeitsteuerung)
                
                # 2. Den neuen Inhalt effizient mit executemany einfügen
                if data_to_write:
                    cursor.executemany(settings.sql_writezeitsteuerung, data_to_write)
        except sqlite3.Error as e:
            logging.error(f"Der Fehler {e} ist beim Schreiben der Zeitsteuerungstabelle aufgetreten")
            raise
    
    @property
    def vZeitsteuerung(self):
        return self.Zeitsteuerungszeilen

    @vZeitsteuerung.setter
    def vZeitsteuerung(self, value: list[dict]):
        self._zeitsteuerungwrite(value)
        # Nach dem Schreiben die Daten neu laden, um den internen Zustand konsistent zu halten.
        self._zeitsteuerungload()
