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
import time

datav=maindata()

# 60 sec schlafen bevor die Programmsteuerung erneut die aktuellen Werte prüft.
sleeptime= 60

def programloop()->None:
    pass


def time_in_range(von:str, bis:str,zeitpunkt:str)->bool:
    '''Prüft ob ein Zeitpunkt innerhalb eines Zeitbereichs liegt'''
    vonstunde, vonminute = von.split(":")
    bisstunde, bisminute = bis.split(":")
    zeitpunktstunde, zeitpunktminute =zeitpunkt.split(":")
    von_value=vonstunde*60+vonminute
    bis_value=bisstunde*60+bisminute
    zeitpunkt_value=zeitpunktstunde*60+zeitpunktminute
    # Mitternacht berücksichtigen
    if von_value < bis_value:
        return von_value <= zeitpunkt_value <= bis_value
    else:
        return (von_value <= zeitpunkt_value) or (zeitpunkt_value <= bis_value)


def day_in_range(programday:int)->bool:
    '''prüft ob der Programmtag/Bereich dem aktuellen Tag entspricht'''
    # Montag ist 1 .... Sonntag ist 7,
    # 8:'Mo-Fr', 9:'Sa-So', 10:'Mo-So' 
    # siehe Definition in gui.py
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

       
def evaluate_program()->None:
    '''Wertet die Programmsteuerungstabelle minütlich aus und setzt/löscht die Variablen für Brauchwasser, Heizung und Nachtabsenkung'''
    # rows=[]
    while(datav.threadstop==True):
        # Programmsteuerungsdaten einlesen
        # typdict = {1:'Brauchw', 2:'Heizen', 3:'Nachtabsenk.'}
        t=datetime.now()
        zeitpunkt=str(t.hour)+':'+str(t.minute)
        # rows.clear()
        # rows= [{'line_id': item[0], 'type':item[1], 'tage':item[2], 'von':item[3], 'bis': item[4], 'active':item[5], 'changetime':item[6]} for item in datav.vZeitsteuerung]          
        # jede Zeile berücksichtigen
        for i in datav.vZeitsteuerung:
            zs=datav.vZeitsteuerung[i]
            match (zs['type']):
                case 'Brauchw':
                    if day_in_range(zs['tage'] and time_in_range(zs['von'],zs['bis'],zeitpunkt)):
                        datav.vBrauchwasserbereiten=True
                    else:
                        datav._Brauchwasserbereiten=False
                        
                case 'Heizen':
                        if day_in_range(zs['tage'] and time_in_range(zs['von'],zs['bis'],zeitpunkt)):
                            datav.vHeizen=True
                        else:
                            datav.vHeizen=False
    
                case 'Nachabsenk.':
                        if day_in_range(zs['tage'] and time_in_range(zs['von'],zs['bis'],zeitpunkt)):
                            datav.vNachtabsenkung=True
                        else:
                            datav.vNachtabsenkung=False
                case _:
                    # Hier sollte niemand vorbeischauen
                    exit(1)
        time.sleep(sleeptime)
    
def start_evaluatethread()->None:
    '''Startet den eigenen Auswertethread der Programmsteuerung'''
    
    x = threading.Thread(target=evaluate_program, name="Thread-Programmsteuerung")
    logging.info('Starte Prgrammsteuerungsthread')
    settings.ThreadList.append(x)
    x.start()
    logging.debug('Programmsteuerungsthread gestartet!')

    