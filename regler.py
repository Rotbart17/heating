#!/usr/bin/env python3
"""Regelkreis-Thread: liest die Messwerte, entscheidet mit control.decide() und schaltet
über die Ausgabeschicht. Läuft im Backendprozess (siehe Regelkreis.txt).
"""
import logging
import math
import threading
import time
from datetime import datetime
from multiprocessing.synchronize import Event
from typing import Callable

import settings
from ausgabe import Ausgabe, Brennerzyklus
from control import Eingang, Grenzen, Modus, decide, ist_winter, kennlinie_soll
from dbinit import connect_db
from dataview import maindata

# Sekunden zwischen zwei Regelschritten
INTERVALL = 10
# ältere Sensorwerte gelten als ausgefallen
MAX_SENSORALTER = 60


def letzter_sensorwert(tabelle: str) -> float:
    '''Letzter Messwert einer Sensortabelle. NaN, wenn es keinen gibt oder er zu alt ist,
    NaN fällt in control.decide() durch die Toleranzprüfung und führt zum Fehler.'''
    with connect_db() as db:
        row = db.execute(
            f"SELECT value, strftime('%s','now','localtime') - strftime('%s', begin_date) "
            f"FROM {tabelle} ORDER BY id DESC LIMIT 1").fetchone()
    if row is None or row[1] > MAX_SENSORALTER:
        return math.nan
    return float(row[0])


def brennerlauf_in_db(von: str, bis: str) -> None:
    with connect_db() as db:
        db.execute(settings.sql_writebrennersensorbetrieb, (True, False, von, bis))


class Regler:
    def __init__(self, stop_event: Event, datav: maindata, ausgabe: Ausgabe,
                 grenzen: Grenzen = Grenzen(),
                 sensorquelle: Callable[[str], float] = letzter_sensorwert,
                 protokoll: Callable[[str, str], None] = brennerlauf_in_db,
                 uhr: Callable[[], float] = time.monotonic) -> None:
        self.stop_event = stop_event
        self.datav = datav
        self.ausgabe = ausgabe
        self.grenzen = grenzen
        self.sensorquelle = sensorquelle
        self.protokoll = protokoll
        self.uhr = uhr
        self.zyklus = Brennerzyklus(uhr())
        self.modus = Modus.AUS
        self._brenner_start: str | None = None

    def _setze(self, name: str, value) -> None:
        '''Schreibt nur geänderte Werte in die DB'''
        if isinstance(value, float):
            value = round(value, 1)
        if getattr(self.datav, name) != value:
            setattr(self.datav, name, value)

    def _lese_eingang(self) -> Eingang:
        d = self.datav
        # das Backend pollt nicht selbst, deshalb hier frisch aus der DB laden
        d._viewloader(False)
        d._kesseldataload()

        kessel = self.sensorquelle(settings.Kesselsensor)
        brauchwasser = self.sensorquelle(settings.Brauchwassersensor)
        aussen = self.sensorquelle(settings.Aussensensor)
        innen = self.sensorquelle(settings.Innensensor)
        for name, wert in (("vKessel", kessel), ("vBrauchwasser", brauchwasser),
                           ("vAussen", aussen), ("vInnen", innen)):
            if not math.isnan(wert):
                self._setze(name, wert)

        winter = d.vWinter
        kessel_soll = d.vKesselSoll
        if not (math.isnan(aussen) or math.isnan(innen)):
            winter = ist_winter(aussen, innen, d.vWintertemp, d.vWintertempInnen, bool(d.vWinter))
            self._setze("vWinter", winter)
            kessel_soll = kennlinie_soll(d.vKesselDaten_x, d.vKesselDaten_y, aussen)
            self._setze("vKesselSoll", kessel_soll)

        return Eingang(
            kessel=kessel, kessel_soll=kessel_soll, brauchwasser=brauchwasser,
            brauchwasser_soll=d.vBrauchwasserSoll, aussen=aussen, innen=innen,
            winter=bool(winter), heizen=bool(d.vHeizen), nachtabsenkung=bool(d.vNachtabsenkung),
            brauchwasser_aus=bool(d.vBrauchwasserAus), brauchwasser_bereiten=bool(d.vBrauchwasserbereiten),
            hand_dusche=bool(d.vHand_Dusche), legionellenschutz=bool(d.vLegionellenschutz),
            brenner_stoerung=bool(d.vBrenner_Stoerung), modus=self.modus, brenner_an=self.ausgabe.brenner)

    def schritt(self) -> None:
        '''Ein Regelschritt'''
        entscheidung = decide(self._lese_eingang(), self.grenzen)
        fehler = entscheidung.modus is Modus.FEHLER
        brenner = self.zyklus.freigabe(entscheidung.brenner, self.uhr(), notaus=fehler)

        pumpen = (entscheidung.pumpe_oben, entscheidung.pumpe_unten, entscheidung.pumpe_brauchwasser)
        if brenner and not entscheidung.brenner:
            # Mindestlaufzeit: der Brenner läuft weiter, also müssen auch die Pumpen weiterlaufen
            pumpen = tuple(neu or alt for neu, alt in zip(pumpen, (
                self.ausgabe.pumpe_oben, self.ausgabe.pumpe_unten, self.ausgabe.pumpe_brauchwasser)))

        if entscheidung.modus is not self.modus or fehler:
            level = logging.WARNING if fehler else logging.INFO
            logging.log(level, f"Regelkreis: {entscheidung.modus.value} {'; '.join(entscheidung.fehler)}")
        self.modus = entscheidung.modus
        self._schalte(*pumpen, brenner)

    def _schalte(self, pumpe_oben: bool, pumpe_unten: bool, pumpe_brauchwasser: bool, brenner: bool) -> None:
        '''Schaltet die Ausgänge, meldet den Zustand an die Anzeige und protokolliert Brennerläufe'''
        self.ausgabe.schalte(pumpe_oben, pumpe_unten, pumpe_brauchwasser, brenner)
        self._setze("vPumpe_oben_an", pumpe_oben)
        self._setze("vPumpe_unten_an", pumpe_unten)
        self._setze("vPumpe_Brauchwasser_an", pumpe_brauchwasser)
        self._setze("vBrenner_an", brenner)
        jetzt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if brenner and self._brenner_start is None:
            self._brenner_start = jetzt
        elif not brenner and self._brenner_start is not None:
            self.protokoll(self._brenner_start, jetzt)
            self._brenner_start = None

    def sicherer_zustand(self) -> None:
        '''Alles aus. Der Brenner wird auch in der Zyklusverwaltung als aus geführt.'''
        self.zyklus.freigabe(False, self.uhr(), notaus=True)
        self._schalte(False, False, False, False)

    def run(self) -> None:
        # Beim Start sind Pumpen und Brenner aus (Regelkreis.txt)
        try:
            self.sicherer_zustand()
            while not self.stop_event.is_set():
                try:
                    self.schritt()
                except Exception:
                    logging.exception("Regelschritt fehlgeschlagen, gehe in den sicheren Zustand")
                    self.sicherer_zustand()
                self.stop_event.wait(INTERVALL)
        finally:
            try:
                self.sicherer_zustand()
            except Exception:
                logging.exception("Sicherer Zustand konnte nicht in die DB geschrieben werden")
                self.ausgabe.alles_aus()
            logging.info("Regelkreisthread ist gestoppt.")


def start_regler(stop_event: Event, ausgabe: Ausgabe | None = None) -> threading.Thread:
    '''Startet den Regelkreisthread'''
    regler = Regler(stop_event, maindata(start_polling=False), ausgabe or Ausgabe())
    thread = threading.Thread(target=regler.run, name="Thread-Regelkreis")
    logging.info('Starte Regelkreisthread')
    thread.start()
    return thread
