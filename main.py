#!/usr/bin/env python3
# diese Datei soll all Prozesse starten
# 1. Backendprozess mit seinen Threads für die Sensoren, Regelkreis, Zeitsteuerung
# 2. den GUI prozess
# Bislang wird hier nur der Backendprozess gestartet
# Es soll einen überwachungsprozess geben, der soll aber von System-d gestartet werden. 

import dbinit
import settings
from sensors import sensor
# import threading
import time
from table import KesselSollTemperatur, Zeitsteuerung, Brennersensor, WorkdataView
import multiprocessing



# startet die GUI und übergibt 2 Queues zur BiDi Kommunikation
def start_gui(queue_to_gui,queue_to_main):
    # Start the GUI process
    process = multiprocessing.Process(target=gui, name="GUI-Prozess", args=(queue_to_gui, queue_to_main))
    return process


def startbackend()-> None:
    dbinit.init_db_environment()
    
    # das könnte ich in init_db verschieben. Da man mit return mehrere Werte zurückgeben kann
    # könnte die Terminierung der Threads auf dieser Ebene bleiben.
    global kss,ass,bws,iss
    kss= sensor(settings.Kesselsensor,settings.sql_create_sensor_table_p1,settings.sql_create_sensor_table_p2)
    ass= sensor(settings.Aussensensor,settings.sql_create_sensor_table_p1,settings.sql_create_sensor_table_p2)
    bws= sensor(settings.Brauchwassersensor,settings.sql_create_sensor_table_p1,settings.sql_create_sensor_table_p2)
    iss= sensor(settings.Innensensor,settings.sql_create_sensor_table_p1,settings.sql_create_sensor_table_p2)
    kst= KesselSollTemperatur(settings.KesselSollTemperatur,settings.sql_kennlinie_p1,settings.sql_kennlinie_p2)
    zst= Zeitsteuerung(settings.ZeitSteuerung,settings.sql_zeitsteuerung_p1,settings.sql_zeitsteuerung_p2)
    bst= Brennersensor(settings.Brennersensor, settings.sql_brennersensor_p1,settings.sql_brennersensor_p2)
    wdv= WorkdataView(settings.WorkDataView, settings.sql_create_view_table_p1, settings.sql_create_view_table_p2)
    

    # print("Das sorgt dafür, dass in der DB auch ne handvoll Daten drin sind.")
    # time.sleep(60)

    # hier muss die GUI gestartet werden
    # queue_to_gui = multiprocessing.Queue()
    # queue_to_main = multiprocessing.Queue()
    # gui_process = start_gui(queue_to_gui,queue_to_main)

    # hier muss der Regelkreis gestartet werden
    # hier muss die Zeitsteuerung gestartet werden
    # der Überwachungsprozess sollte aus system-d gestartet werden.


    # hier ziehen wir dann wieder die Bremse
    
def stopbackend(stop:bool):

    kss.threadstop=stop
    ass.threadstop=stop
    bws.threadstop=stop
    iss.threadstop=stop
    # queue_to_gui.put("processstop")

#     zst.threadstop=True
#     bst.threadstop=True
    print("ich bin echt neugierig!")
    time.sleep(5)

    # Ende Funktionen
    # Threads wieder einsammeln
    for i in settings.ThreadList:
        i.join(timeout=2)

    # GUI Prozess wieder einsammeln
    # gui_process.join()


# if __name__ == '__main__':
    
#    main()
#    print("Ende!")
    
