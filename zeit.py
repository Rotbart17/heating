#!/usr/bin/env python3
# dieses Modul setzt die Werte für den Regelkreis die sich durch die Programmsteuerung ändern
# Eigenen Thread eröffnen
# Schleife die nur bei threadstop beendet wird
# prüfen ab man die aktuellen Programmsteurungsdaten hat
# Programmsteuerungsdaten lesen
# Werte für den Vergleich adaptieren
# Vergleich mit dem Tag(en) beginnen
#   Wenn das passt den Uhrzeitbereich abchecken
#       Wenn das passt dann die entsprechende Variable setzen
#       Wenn es nicht passt die entsprechende Variable löschen 
# Hand/Dusche hat einen Vorrang vor dem Heizbetrieb. Das muss aber im Regelkreis berücksichtigt werden.
# Fähigkeiten:
# Werte: Brauchwasser an / aus, Heizung an / aus, Nachtabsenkung an / aus
# Schlafen
from datetime import datetime
import logging
import threading
import settings
from table import Tables
import random
from dataview import maindata
import time
from multiprocessing import Queue
from queue import Empty



# 60 sec schlafen bevor die Programmsteuerung erneut die aktuellen Werte prüft.
sleeptime= 60


def sleep_until_stop(seconds: float)->None:
    end_time = time.monotonic() + seconds
    while datav.threadstop == False:
        remaining = end_time - time.monotonic()
        if remaining <= 0:
            return
        time.sleep(min(0.5, remaining))


def _time_to_minutes(value: str) -> int:
    hour, minute = value.split(":", maxsplit=1)
    return int(hour) * 60 + int(minute)


def time_in_range(von:str, bis:str,zeitpunkt:str)->bool:
    '''Prüft ob ein Zeitpunkt innerhalb eines Zeitbereichs liegt. Zeit in Form von hh:mm'''
    von_value=_time_to_minutes(von)
    bis_value=_time_to_minutes(bis)
    zeitpunkt_value=_time_to_minutes(zeitpunkt)
    # Mitternacht berücksichtigen
    if von_value < bis_value:
        return von_value <= zeitpunkt_value <= bis_value
    else:
        return (von_value <= zeitpunkt_value) or (zeitpunkt_value <= bis_value)


def day_in_range(programday)->bool:
    '''prüft ob der Programmtag/Bereich dem aktuellen Tag entspricht'''
    # Montag ist 1 .... Sonntag ist 7,
    # 8:'Mo-Fr', 9:'Sa-So', 10:'Mo-So' 
    # siehe Definition in gui.py
    dayofWeek=datetime.today().isoweekday()
    day_labels = {
        1: 'Mo',
        2: 'Die',
        3: 'Mi',
        4: 'Do',
        5: 'Fr',
        6: 'Sa',
        7: 'So',
    }
    if isinstance(programday, str):
        programday = programday.strip()
        if programday == 'Mo-Fr':
            return dayofWeek <= 5
        if programday == 'Sa-So':
            return dayofWeek >= 6
        if programday == 'Mo-So':
            return True
        return day_labels[dayofWeek] == programday

    if programday <= 7:
        return dayofWeek == programday
    if programday > 7:  
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
    return (False)  


def _zeitsteuerung_row_as_dict(row):
    if isinstance(row, dict):
        return row.copy()

    line_id, typ, tage, von, bis, active, changetime = row
    return {
        'line_id': line_id,
        'type': typ,
        'tage': tage,
        'von': von,
        'bis': bis,
        'active': active,
        'changetime': changetime,
    }

       
def evaluate_program(queue_to_backend:Queue, _queue_from_backend:Queue)->None:
    '''Wertet die Programmsteuerungstabelle minütlich aus und setzt/löscht die Variablen für Brauchwasser, Heizung und Nachtabsenkung'''
    
    while(datav.threadstop==False):
        # Programmsteuerungsdaten einlesen
        # typdict = {1:'Brauchw', 2:'Heizen', 3:'Nachtabsenk.'}
        t=datetime.now()
        zeitpunkt=f'{t.hour:02d}:{t.minute:02d}'
        # rows.clear()
        # rows= [{'line_id': item[0], 'type':item[1], 'tage':item[2], 'von':item[3], 'bis': item[4], 'active':item[5], 'changetime':item[6]} for item in datav.vZeitsteuerung]          
        program_states = {
            'Brauchw': False,
            'Heizen': False,
            'Nachtabsenk.': False,
        }
        zeitsteuerung_rows = []
        active_changed = False

        for row in datav.vZeitsteuerung:
            zs = _zeitsteuerung_row_as_dict(row)
            try:
                active = day_in_range(zs['tage']) and time_in_range(zs['von'],zs['bis'],zeitpunkt)
            except (KeyError, TypeError, ValueError) as e:
                active = False
                logging.error(f"Zeitsteuerungszeile {zs} konnte nicht ausgewertet werden: {e}")

            active_changed = active_changed or zs['active'] != active
            zs['active'] = active
            match (zs['type']):
                case 'Brauchw':
                    program_states['Brauchw'] = program_states['Brauchw'] or active
                        
                case 'Heizen':
                    program_states['Heizen'] = program_states['Heizen'] or active
    
                case 'Nachabsenk.':
                    program_states['Nachtabsenk.'] = program_states['Nachtabsenk.'] or active
                case _:
                    # Hier sollte niemand vorbeischauen
                    logging.error(f"Der ausgewählte Heiztyp  {zs['type']} ist unbekannt!")

            zeitsteuerung_rows.append(zs)

        if active_changed:
            datav.vZeitsteuerung = zeitsteuerung_rows
        if datav.vBrauchwasserbereiten != program_states['Brauchw']:
            datav.vBrauchwasserbereiten = program_states['Brauchw']
        if datav.vHeizen != program_states['Heizen']:
            datav.vHeizen = program_states['Heizen']
        if datav.vNachtabsenkung != program_states['Nachtabsenk.']:
            datav.vNachtabsenkung = program_states['Nachtabsenk.']
        sleep_until_stop(sleeptime)
        try:
            message = queue_to_backend.get(timeout=1)
            if message=="threadstop":
                datav.threadstop=True
                logging.info(f"evaluatethread ist gestoppt.")
        except Empty:
            continue
        
 
 
    
def start_evaluatethread(queue_to_backend:Queue, queue_from_backend:Queue):

    '''Startet den eigenen Auswertethread der Programmsteuerung'''
    global datav 
    datav=maindata()
    datav.queue_to_backend=queue_from_backend
    datav.queue_to_frontend=queue_to_backend
   
    x = threading.Thread(target=evaluate_program, name="Thread-Programmsteuerung", args=(queue_to_backend,queue_from_backend))
    logging.info('Starte Programmsteuerungsthread')
    settings.ThreadList.append(x)
    x.start()
    logging.debug('Programmsteuerungsthread gestartet!')
    #jetzt ist hier alles gestartet, damit Info an die GUI
    queue_from_backend.put("start_evaluatethread"+"_up")
    return datav

    
