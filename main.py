#!/usr/bin/env python3
# diese Datei soll alle Backend-Prozesse starten. Sie wird von gui.py als eigener Prozess aufgerufen
# Backendprozess mit seinen Threads für die Sensoren, Regelkreis, Zeitsteuerung, Datenschicht für die Kommunikation
# Es soll einen überwachungsprozess geben, der soll aber von System-d gestartet werden. 

import dbinit
import logging
import settings
from sensors import sensor
# import threading
import time
from table import KesselSollTemperatur, Zeitsteuerung, Brennersensor, WorkdataView
from multiprocessing import Queue
from queue import Empty
from zeit import start_evaluatethread

BACKEND_READY = "backend_up"
STOP_MESSAGE = "threadstop"


def startbackend(queue_to_backend:Queue, queue_from_backend:Queue)-> None:
    '''Startet alle Backendthreads'''
    program_data = None

    try:
        dbinit.init_db_environment()

        global kss,ass,bws,iss
        kss= sensor(settings.Kesselsensor, settings.sql_create_sensor_table_columns, queue_to_backend, queue_from_backend)
        ass= sensor(settings.Aussensensor, settings.sql_create_sensor_table_columns, queue_to_backend, queue_from_backend)
        bws= sensor(settings.Brauchwassersensor, settings.sql_create_sensor_table_columns, queue_to_backend, queue_from_backend)
        iss= sensor(settings.Innensensor, settings.sql_create_sensor_table_columns, queue_to_backend, queue_from_backend)
        kst= KesselSollTemperatur(settings.KesselSollTemperatur, settings.sql_kennlinie_columns, queue_to_backend, queue_from_backend)
        zst= Zeitsteuerung(settings.ZeitSteuerung, settings.sql_zeitsteuerung_columns, queue_to_backend, queue_from_backend)
        bst= Brennersensor(settings.Brennersensor, settings.sql_brennersensor_columns, queue_to_backend, queue_from_backend)
        wdv= WorkdataView(settings.WorkDataView, settings.sql_create_view_table_columns, queue_to_backend, queue_from_backend)
        program_data = start_evaluatethread(queue_to_backend, queue_from_backend)
        queue_from_backend.put(BACKEND_READY)

        wait_for_stop_signal(queue_to_backend, program_data)
    finally:
        stopbackend(True, program_data)

    # der Überwachungsprozess sollte aus system-d gestartet werden.


def wait_for_stop_signal(queue_to_backend:Queue, program_data)->None:
    '''Wartet auf das Stop-Signal der GUI.'''
    while getattr(program_data, 'threadstop', False) == False:
        try:
            message = queue_to_backend.get(timeout=1)
        except Empty:
            continue

        if message == STOP_MESSAGE:
            return

        queue_to_backend.put_nowait(message)
        time.sleep(0.1)


# hier ziehen wir dann wieder die Bremse    
def stopbackend(stop:bool, program_data=None)->None:
    '''Stoppt alle Backendthreads'''
    settings.threadstop=stop

    for sensor_object in settings.SensorList:
        sensor_object.threadstop=stop

    if program_data is not None:
        program_data.threadstop=stop

    # Ende Funktionen
    # Threads wieder einsammeln
    for backend_thread in settings.ThreadList:
        if backend_thread.ident is None:
            continue
        backend_thread.join(timeout=2)
        if backend_thread.is_alive():
            logging.warning(f"Thread {backend_thread.name} konnte nicht innerhalb des Timeouts beendet werden.")
    print("Alles perfekt zu Ende!")
