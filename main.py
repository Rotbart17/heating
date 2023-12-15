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
    print("Nix war los")
    print("schauen wir Mal ob das mit dem Thread nun funktioniert")
    time.sleep(30)
    sensors.sensor.threadstop=True
    print("ich bin echt neugierig!")
    time.sleep(10)

    # Ende Funktionen
    # Threads wieder einsammeln
    for i in settings.ThreadList:
        i.join(timeout=2)

  




if __name__ == '__main__':
    
    main()
    print("Ende!")
    
