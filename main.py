# DB muss erstellt werden wenn nötig so wie der Zugriff auf die Tabellen
import dbinit
import settings
import sensors
import threading
import time

# Constanten

def main():
    ks= sensors.kesselsensor("Kesselsensor")
    ks2= sensors.kesselsensor("Kesselsensor2")
    print("Nix war los")
    print("schauen wir Mal ob das mit dem Thread nun funktioniert")
    time.sleep(30)
    sensors.sensor.threadstop=True
    print("ich bin echt neugierig!")
    time.sleep(20)

    # Ende Funktionen
    # Threads wieder einsammeln
    for i in settings.ThreadList:
        i.join(timeout=2)

  




if __name__ == '__main__':
    
    main()
    
