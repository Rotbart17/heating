# DB muss erstellt werden wenn nötig so wie der Zugriff auf die Tabellen
import dbinit
import settings
import sensors


# Constanten

def main():
    ks= sensors.kesselsensor("Kesselsensor")
    print("Nix war los")
    print("schauen wir Mal ob das mit them Thread nun fnktioniert")
    sensors.sensor.threadstop=True
    print("ich bin echt neugierig!")
    



if __name__ == '__main__':
    
    main()
    
