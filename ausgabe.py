#!/usr/bin/env python3
"""Ausgabeschicht des Regelkreises: Pumpen und Brenner schalten.

Die Entscheidung kommt aus control.decide(). Hier wird sie umgesetzt, und die
Brenner-Mindestlaufzeit und -Totzeit werden durchgesetzt.
"""
import logging


class Ausgabe:
    '''Schaltet Pumpen und Brenner. Für echte Hardware (z.B. GPIO-Relais) hiervon ableiten
    und _setze_hardware() überschreiben. Dort muss der Brenner vor den Pumpen
    abgeschaltet und nach den Pumpen eingeschaltet werden.'''

    def __init__(self) -> None:
        self.pumpe_oben = False
        self.pumpe_unten = False
        self.pumpe_brauchwasser = False
        self.brenner = False

    def schalte(self, pumpe_oben: bool, pumpe_unten: bool, pumpe_brauchwasser: bool, brenner: bool) -> None:
        neu = (pumpe_oben, pumpe_unten, pumpe_brauchwasser, brenner)
        if neu == (self.pumpe_oben, self.pumpe_unten, self.pumpe_brauchwasser, self.brenner):
            return
        self._setze_hardware(*neu)
        self.pumpe_oben, self.pumpe_unten, self.pumpe_brauchwasser, self.brenner = neu
        logging.info(f"Ausgabe: Pumpe oben={neu[0]} unten={neu[1]} Brauchwasser={neu[2]} Brenner={neu[3]}")

    def alles_aus(self) -> None:
        self.schalte(False, False, False, False)

    def _setze_hardware(self, pumpe_oben: bool, pumpe_unten: bool, pumpe_brauchwasser: bool, brenner: bool) -> None:
        '''Simulation: keine Hardware'''


class Brennerzyklus:
    '''Erzwingt Mindestlaufzeit und Mindestpause (Totzeit) des Brenners, Zeiten in Sekunden.
    Nach dem Start gilt die Pause, denn wann der Brenner zuletzt lief, ist unbekannt.'''

    def __init__(self, jetzt: float, min_lauf: float = 300, min_pause: float = 300) -> None:
        self.min_lauf = min_lauf
        self.min_pause = min_pause
        self.an = False
        self._seit = jetzt

    def freigabe(self, wunsch: bool, jetzt: float, notaus: bool = False) -> bool:
        '''Liefert, ob der Brenner laufen darf. Ein Notaus (Fehler) schaltet sofort ab.'''
        if self.an:
            if notaus or (not wunsch and jetzt - self._seit >= self.min_lauf):
                self.an = False
                self._seit = jetzt
        elif wunsch and not notaus and jetzt - self._seit >= self.min_pause:
            self.an = True
            self._seit = jetzt
        return self.an
