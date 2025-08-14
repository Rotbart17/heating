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
    def _kesseldataload(self):
        """Lädt die Kesselkennlinie (x- und y-Werte) aus der Datenbank."""
        try:
            with sqlite3.connect(settings.DBPATH) as db:
                logging.debug('Kesselkennlinie lesen!')
                cursor = db.cursor()
                # Es ist effizienter, beide Spalten auf einmal abzurufen und die Reihenfolge sicherzustellen.
                sql = f"SELECT value_x, value_y FROM {settings.KesselSollTemperatur} ORDER BY id;"
                cursor.execute(sql)
                results = cursor.fetchall()
                if results:
                    # Entpackt die Liste von Tupeln in zwei separate Listen
                    self._KesselDaten_x, self._KesselDaten_y = zip(*results)
                    # zip gibt Tupel zurück, wir konvertieren sie in Listen
                    self._KesselDaten_x = list(self._KesselDaten_x)
                    self._KesselDaten_y = list(self._KesselDaten_y)
                else:
                    self._KesselDaten_x = []
                    self._KesselDaten_y = []
        except sqlite3.Error as e:
            logging.error(f"Der Fehler {e} ist beim Lesen der Kesselkennlinie aufgetreten")
            exit(1)


    def _writeKesselDaten_y(self, value):
        """Speichert die y-Werte der Kesselkennlinie in der Datenbank."""
        self._KesselDaten_y = value.copy()
        try:
            # Die 'with'-Anweisung stellt eine transaktionale Operation sicher (automatisches Commit/Rollback)
            # und schließt die Verbindung.
            with sqlite3.connect(settings.DBPATH) as db:
                logging.debug('Kesselkennline (y-Werte) in DB schreiben!')
                # Daten für eine effizientere `executemany`-Operation vorbereiten
                data_to_update = [(y_value, idx + 1) for idx, y_value in enumerate(self._KesselDaten_y)]
                db.executemany(settings.sql_write_KesselKennlinie_y, data_to_update)
        except sqlite3.Error as e:
            logging.error(f"Der Fehler {e} ist beim Schreiben der Kesselkennlinie_y aufgetreten")
            exit(1)
