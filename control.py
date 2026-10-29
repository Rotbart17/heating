#!/usr/bin/env python3
"""Entscheidungslogik der Regelkreise (siehe Regelkreis.txt).

Die Funktion decide() ist reine Logik: Messwerte und Zustand rein, Entscheidung raus.
Sie greift weder auf die Datenbank noch auf die Hardware zu. Die Ausgabeschicht
(Pumpen, Brenner, Anzeige, Mail) setzt die Entscheidung um.

Alle Aktionen dürfen nur stattfinden, wenn alle Werte innerhalb der Toleranzen sind.
Wenn nicht, wird FEHLER entschieden: Brenner und Pumpen aus, bis die Werte wieder
im Normbereich sind.

Prioritäten (höchste zuerst): Gefrierschutz, Legionellenschutz, Brauchwasser, Heizen.
Brenner-Mindestlaufzeit und -Totzeit sind Sache der Ausgabeschicht, hier wird nur
der Brennerwunsch (brenner) entschieden.
"""
from dataclasses import dataclass, field
from enum import Enum


class Modus(Enum):
    AUS = "Aus"
    FEHLER = "Fehler"
    GEFRIERSCHUTZ = "Gefrierschutz"
    LEGIONELLENSCHUTZ = "Legionellenschutz"
    BRAUCHWASSER = "Brauchwasser"
    HEIZEN = "Heizen"


@dataclass(frozen=True)
class Grenzen:
    '''Toleranzen und Schwellwerte. Die Defaults entsprechen Regelkreis.txt.'''
    kessel_min: float = 2
    kessel_max: float = 90
    brauchwasser_min: float = 2
    brauchwasser_error: float = 70
    aussen_min: float = -30
    aussen_max: float = 30
    innen_min: float = 2
    innen_max: float = 30
    # Hysterese für Heizen und Gefrierschutz
    hysterese: float = 2
    # Hysterese, bevor die Brauchwasserbereitung startet
    brauchwasser_hysterese: float = 5
    legionellen_soll: float = 65
    frost_aussen: float = 3
    frost_kessel: float = 10
    frost_innen: float = 5
    # unter dieser Kesseltemperatur wird im Gefrierschutz der Brenner gestartet
    frost_kessel_brenner: float = 5
    # Nachtabsenkung: Verringerung der Kesselsolltemperatur
    nachtabsenkung: float = 10


@dataclass(frozen=True)
class Eingang:
    '''Alles, was die Entscheidung braucht'''
    kessel: float
    kessel_soll: float
    brauchwasser: float
    brauchwasser_soll: float
    aussen: float
    innen: float
    winter: bool
    heizen: bool
    nachtabsenkung: bool
    brauchwasser_aus: bool
    brauchwasser_bereiten: bool
    hand_dusche: bool
    legionellenschutz: bool
    brenner_stoerung: bool
    # Modus der letzten Entscheidung und Brennerstatus, nötig für die Hysterese
    modus: Modus = Modus.AUS
    brenner_an: bool = False


@dataclass(frozen=True)
class Entscheidung:
    modus: Modus
    pumpe_oben: bool = False
    pumpe_unten: bool = False
    pumpe_brauchwasser: bool = False
    brenner: bool = False
    fehler: list[str] = field(default_factory=list)


def pruefe_toleranzen(e: Eingang, g: Grenzen) -> list[str]:
    '''Liefert die Fehlertexte aller Werte außerhalb der Toleranz'''
    fehler = []
    if not g.kessel_min < e.kessel < g.kessel_max:
        fehler.append(f"Kesseltemperatur {e.kessel} außerhalb {g.kessel_min}..{g.kessel_max}")
    if not g.brauchwasser_min < e.brauchwasser < g.brauchwasser_error:
        fehler.append(f"Brauchwassertemperatur {e.brauchwasser} außerhalb {g.brauchwasser_min}..{g.brauchwasser_error}")
    if not g.aussen_min < e.aussen < g.aussen_max:
        fehler.append(f"Außentemperatur {e.aussen} außerhalb {g.aussen_min}..{g.aussen_max}")
    if not g.innen_min < e.innen < g.innen_max:
        fehler.append(f"Innentemperatur {e.innen} außerhalb {g.innen_min}..{g.innen_max}")
    if e.brenner_stoerung:
        fehler.append("Brennerstörung")
    return fehler


def _gefrierschutz(e: Eingang, g: Grenzen) -> Entscheidung | None:
    '''Prio 1: Umwälzen, wenn es kalt ist. Brenner nur, wenn der Kessel wirklich auskühlt.'''
    aktiv = e.modus is Modus.GEFRIERSCHUTZ
    zuschlag = g.hysterese if aktiv else 0
    kalt = (e.aussen < g.frost_aussen + zuschlag
            and e.kessel < g.frost_kessel + zuschlag
            and e.innen < g.frost_innen + zuschlag)
    if not kalt:
        return None
    brenner_grenze = g.frost_kessel_brenner + (g.hysterese if aktiv else 0)
    return Entscheidung(Modus.GEFRIERSCHUTZ, pumpe_oben=True, pumpe_unten=True,
                        brenner=e.kessel < brenner_grenze)


def _brauchwasser(e: Eingang, g: Grenzen, soll: float, modus: Modus) -> Entscheidung | None:
    '''Brauchwasserbereitung bis soll. Heizungspumpen sind dabei aus.
    Der Kessel muss über dem Speicher liegen, sonst muss der Brenner laufen.'''
    aktiv = e.modus is modus
    if aktiv:
        noetig = e.brauchwasser < soll
    else:
        noetig = e.brauchwasser < soll - g.brauchwasser_hysterese
    if not noetig:
        return None
    return Entscheidung(modus, pumpe_brauchwasser=True, brenner=e.kessel < soll + 10)


def _heizen(e: Eingang, g: Grenzen) -> Entscheidung | None:
    '''Prio 4: Heizbetrieb nur im Winter und nur, wenn das Programm es verlangt'''
    if not (e.winter and e.heizen):
        return None
    soll = e.kessel_soll - (g.nachtabsenkung if e.nachtabsenkung else 0)
    # Brenner aus bei soll + Hysterese, erst wieder an bei soll - Hysterese
    brenner = e.kessel < (soll + g.hysterese if e.brenner_an else soll - g.hysterese)
    return Entscheidung(Modus.HEIZEN, pumpe_oben=True, pumpe_unten=True, brenner=brenner)


def decide(e: Eingang, g: Grenzen = Grenzen()) -> Entscheidung:
    '''Entscheidet anhand der Eingangswerte, was laufen soll'''
    fehler = pruefe_toleranzen(e, g)
    if fehler:
        return Entscheidung(Modus.FEHLER, fehler=fehler)

    entscheidung = _gefrierschutz(e, g)
    if entscheidung:
        return entscheidung

    if not e.brauchwasser_aus:
        if e.legionellenschutz:
            entscheidung = _brauchwasser(e, g, g.legionellen_soll, Modus.LEGIONELLENSCHUTZ)
            if entscheidung:
                return entscheidung
        if e.brauchwasser_bereiten or e.hand_dusche:
            entscheidung = _brauchwasser(e, g, e.brauchwasser_soll, Modus.BRAUCHWASSER)
            if entscheidung:
                return entscheidung

    entscheidung = _heizen(e, g)
    if entscheidung:
        return entscheidung

    return Entscheidung(Modus.AUS)
