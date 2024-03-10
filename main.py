#!/usr/bin/env python3
# diese Datei soll all Prozesse starten
# 1. Backendprozess mit seinen Threads für die Sensoren, Regelkreis, Zeitsteuerung
# 2. den GUI prozess
# Bislang wird hier nur der Backendprozess gestartet
# Es soll einen überwachungsprozess geben, der soll aber von System-d gestartet werden. 

import dbinit
import settings
from sensors import sensor
import threading
import time
from table import KesselSollTemperatur, Zeitsteuerung, Brennersensor

# Constanten



def main():
    dbinit.init_db_environment()
    
    # das könnte ich in init_DB_verschieben. Da man mit return mehrere Werte zurückgeben kann
    # könnte die Terminierung der Threads auf dieser Ebene bleiben.
    kss= sensor(settings.Kesselsensor,settings.sql_create_sensor_table_p1,settings.sql_create_sensor_table_p2)
    ass= sensor(settings.Aussensensor,settings.sql_create_sensor_table_p1,settings.sql_create_sensor_table_p2)
    bws= sensor(settings.Brauchwassersensor,settings.sql_create_sensor_table_p1,settings.sql_create_sensor_table_p2)
    iss= sensor(settings.Innensensor,settings.sql_create_sensor_table_p1,settings.sql_create_sensor_table_p2)
    kst= KesselSollTemperatur(settings.KesselSollTemperatur,settings.sql_kennlinie_p1,settings.sql_kennlinie_p2)
    zst= Zeitsteuerung(settings.ZeitSteuerung,settings.sql_zeitsteuerung_p1,settings.sql_zeitsteuerung_p2)
    bst= Brennersensor(settings.Brennersensor, settings.sql_brennersensor_p1,settings.sql_brennersensor_p2)
    

    print("Das sorgt dafür, dass in der DB auch ne handvoll Daten drin sind.")
    time.sleep(200)

    # hier muss die GUI gestartet werden
    # hier muss der Regelkreis gestartet werden
    # hier muss die Zeitsteuerung gestartet werden
    # der Überwachungsprozess sollte aus system-d gestartet werden.


    # hier ziehen wir dann wieder die Bremse
    
    kss.threadstop=True
    ass.threadstop=True
    bws.threadstop=True
    iss.threadstop=True
    zst.threadstop=True
    bst.threadstop=True
    print("ich bin echt neugierig!")
    time.sleep(5)

    # Ende Funktionen
    # Threads wieder einsammeln
    for i in settings.ThreadList:
        i.join(timeout=2)

  




if __name__ == '__main__':
    
    main()
    print("Ende!")
    
