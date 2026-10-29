#!/usr/bin/env python3
# diese Datei soll alle Backend-Prozesse starten. Sie wird von gui.py als eigener Prozess aufgerufen
# Backendprozess mit seinen Threads für die Sensoren, Regelkreis, Zeitsteuerung, Datenschicht für die Kommunikation
# Es soll einen überwachungsprozess geben, der soll aber von System-d gestartet werden. 

import dbinit
import logging
import settings
from sensors import sensor
from table import KesselSollTemperatur, Zeitsteuerung, Brennersensor, WorkdataView
from multiprocessing.synchronize import Event
from zeit import start_evaluatethread


def startbackend(stop_event:Event, ready_event:Event)-> None:
    '''Startet alle Backendthreads.
    stop_event: wird von der GUI gesetzt, um das Backend zu beenden.
    ready_event: wird gesetzt, sobald alle Backendthreads laufen.'''
    try:
        dbinit.init_db_environment()

        for name in (settings.Kesselsensor, settings.Aussensensor, settings.Brauchwassersensor, settings.Innensensor):
            sensor(name, settings.sql_create_sensor_table_columns, stop_event)
        KesselSollTemperatur(settings.KesselSollTemperatur, settings.sql_kennlinie_columns, stop_event)
        Zeitsteuerung(settings.ZeitSteuerung, settings.sql_zeitsteuerung_columns, stop_event)
        Brennersensor(settings.Brennersensor, settings.sql_brennersensor_columns, stop_event)
        WorkdataView(settings.WorkDataView, settings.sql_create_view_table_columns, stop_event)
        program_data = start_evaluatethread(stop_event)
        ready_event.set()

        # warten bis die GUI das Stop-Signal setzt
        stop_event.wait()
    finally:
        stopbackend(stop_event, locals().get('program_data'))

    # der Überwachungsprozess sollte aus system-d gestartet werden.


def stopbackend(stop_event:Event, program_data=None)->None:
    '''Stoppt alle Backendthreads und sammelt sie wieder ein'''
    stop_event.set()

    if program_data is not None:
        program_data.threadstop=True

    for backend_thread in settings.ThreadList:
        if backend_thread.ident is None:
            continue
        backend_thread.join(timeout=2)
        if backend_thread.is_alive():
            logging.warning(f"Thread {backend_thread.name} konnte nicht innerhalb des Timeouts beendet werden.")
    print("Alles perfekt zu Ende!")
