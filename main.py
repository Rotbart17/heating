#!/usr/bin/env python3
# diese Datei soll alle Backend-Prozesse starten. Sie wird von gui.py als eigener Prozess aufgerufen
# Backendprozess mit seinen Threads für die Sensoren, Regelkreis, Zeitsteuerung, Datenschicht für die Kommunikation
# Es soll einen überwachungsprozess geben, der soll aber von System-d gestartet werden. 

import dbinit
import logging
import settings
from sensors import sensor
from table import KesselSollTemperatur, Zeitsteuerung, Brennersensor, WorkdataView
import threading
from dataview import maindata
from multiprocessing.synchronize import Event
from zeit import start_evaluatethread


class Backend:
    '''Besitzt alle Backendthreads und Tabellen und steuert Start und Stop.
    stop_event: wird von der GUI gesetzt, um das Backend zu beenden.
    ready_event: wird gesetzt, sobald alle Backendthreads laufen.'''

    def __init__(self, stop_event:Event, ready_event:Event) -> None:
        self.stop_event = stop_event
        self.ready_event = ready_event
        self.threads: list[threading.Thread] = []
        self.program_data: maindata | None = None

    def start(self) -> None:
        '''Legt die Tabellen an und startet alle Backendthreads'''
        dbinit.init_db_environment()
        stop_event = self.stop_event

        KesselSollTemperatur(settings.KesselSollTemperatur, settings.sql_kennlinie_columns, stop_event)
        Zeitsteuerung(settings.ZeitSteuerung, settings.sql_zeitsteuerung_columns, stop_event)
        Brennersensor(settings.Brennersensor, settings.sql_brennersensor_columns, stop_event)
        WorkdataView(settings.WorkDataView, settings.sql_create_view_table_columns, stop_event)
        for name in (settings.Kesselsensor, settings.Aussensensor, settings.Brauchwassersensor, settings.Innensensor):
            self.threads.append(sensor(name, settings.sql_create_sensor_table_columns, stop_event).thread)
        thread, self.program_data = start_evaluatethread(stop_event)
        self.threads.append(thread)
        self.ready_event.set()

    def stop(self) -> None:
        '''Stoppt alle Backendthreads und sammelt sie wieder ein'''
        self.stop_event.set()
        if self.program_data is not None:
            self.program_data.threadstop = True

        for backend_thread in self.threads:
            if backend_thread.ident is None:
                continue
            backend_thread.join(timeout=2)
            if backend_thread.is_alive():
                logging.warning(f"Thread {backend_thread.name} konnte nicht innerhalb des Timeouts beendet werden.")
        print("Alles perfekt zu Ende!")

    def run(self) -> None:
        '''Startet das Backend und wartet auf das Stop-Signal'''
        try:
            self.start()
            self.stop_event.wait()
        finally:
            self.stop()


def startbackend(stop_event:Event, ready_event:Event)-> None:
    '''Einstiegspunkt des Backendprozesses'''
    Backend(stop_event, ready_event).run()

    # der Überwachungsprozess sollte aus system-d gestartet werden.
