# DB muss erstellt werden wenn nötig so wie der Zugriff auf die Tabellen
import dbinit
import settings
import sensors
import threading
import time

# Constanten



def main():
    dbinit.init_db_environment()
    
    kss= sensors.sensor("Kesselsensor")
    ass= sensors.sensor("Aussensensor")
    bws= sensors.sensor("Brauchwassersensor")
    iss= sensors.sensor("Innensensor")
    

    print("Das sorgt dafür, dass in der DB auch ne handvoll Daten drin sind.")
    time.sleep(200)

    # hier muss die GUI gestartet werden
    # hier muss der Regelkreisgestartet werden
    # der Überwachungsprozess sollte aus syste-D gestartet werden.


    # hier ziehen wir dann wieder die Bremse
    sensors.sensor.threadstop=True
    print("ich bin echt neugierig!")
    time.sleep(5)

    # Ende Funktionen
    # Threads wieder einsammeln
    for i in settings.ThreadList:
        i.join(timeout=2)

  




if __name__ == '__main__':
    
    main()
    print("Ende!")
    
