#!/usr/bin/env python3
# dieses Modul setzt die Werte für den Regelkreis die sich durch die Programmsteuerung ändern
# Eigenen Thread eröffnen
# Schleife die nur bei threadstop beendet wird
# prüfen ab man die aktuellen Programmsterungsdaten hat
# Programmsteuerungsdaten lesen
# Werte für den Vergleich adaptieren
# Vergleich mit dem Tag(en) beginnen
#   Wenn das passt den Uhrzeitbereich abchecken
#       Wenn das passt dann die entsprechende Variable setzen
#       Wenn es nicht passt die entsprechende Variable löschen 
# Hand/Dusche hat einen Vorrang vor der Heizung. Das muss aber im Regelkreis berücksichtigt werden.
# Werte: Brauchwasser an / aus, Heizung an / aus, Nachtabsenkung an / aus
# Schlafen
import datetime
import logging
import threading
import settings
from table import Tables
import random
from dataview import maindata

datav=maindata()

def programloop()->None:
    pass

# prüft ob ein Zeitpunkt innerhalb eines Zeitbereichs liegt
def time_in_range(von:str, bis:str,zeitpunkt:str)->bool:
    vonstunde, vonminute =von.split(":")
    bisstunde, bisminute= bis.split(":")
    zeitpunktstunde, zeitpunktminute =zeitpunkt.split(":")
    von_value=vonstunde*60+vonminute
    bis_value=bisstunde*60+bisminute
    zeitpunkt_value=zeitpunktstunde*60+zeitpunktminute
    # Mitternacht berücksichtigen
    if von_value < bis_value:
        return von_value <= zeitpunkt_value <= bis_value
    else:
        return (von_value <= zeitpunkt_value) or (zeitpunkt_value <= bis_value)

# prüft ob der Programmtag/Bereich dem aktuellen Tag entspricht
def day_in_range(programday:int)->bool:
    # Montag ist 1 .... Sonntag ist 7,
    # 8:'Mo-Fr', 9:'Sa-So', 10:'Mo-So' 
    # siehe definition in gui.py
    dayofWeek=datetime.datetime.today().isoweekday()
    if programday<=7:
        return dayofWeek==programday
    else:
        # Mo-Fr
        if programday == 8:
            if dayofWeek <=5:
                return (True)
            else:
                return (False)
        # Sa und So
        if programday == 9:
            if dayofWeek >=6:
                return (True)
            else:
                return(False)
        # Mo-So
        if programday == 10:
            return (True)
        
                
        
        
    
    
    