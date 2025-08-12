#!/usr/bin/env python3
# in diesem Modul wird die Datenaustauschstruktur definiert
# sie versteckt die Datenbankzugriffe in einer Klasse
# so zumindest die Idee!

import settings
from dataclasses import dataclass, field
import logging
from dbinit import checktable
import threading
import time
import sqlite3
from enum import Enum
from dataview_sensor import SensorView, sens
from dataview_kessel import KesselView
from dataview_zeitst import ZeitView
from multiprocessing import Queue
from typing import Any


# Muster für logging
# logging.debug('debug')
# logging.info('info')
# logging.warning('warning')
# logging.error('error')
# logging.critical('critical')

logging.basicConfig(
    filename='gui.log',
    filemode='w',
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.ERROR
)

def str2bool(value):
    return {"True": True, "true": True}.get(value, False)

class dv(Enum):
    ViewChanged=1
    Winter=2
    Winter_changetime=3
    Wintertemp=4
    Wintertemp_changetime=5
    Kessel=6
    Kessel_changetime=7
    KesselSoll=8
    KesselSoll_changetime=9
    Heizen=10
    Heizen_changetime=11
    Nachtabsenkung=12
    Nachtabsenkung_changetime=13
    Brauchwasser=14
    Brauchwasser_changetime=15
    BrauchwasserSoll=16
    BrauchwasserSoll_changetime=17
    BrauchwasserAus=18
    BrauchwasserAus_changetime=19
    Brauchwasserbereiten=20
    Brauchwasserbereiten_changetime=21
    Innen=22
    Innen_changetime=23
    Aussen=24
    Aussen_changetime=25
    Pumpe_oben_an=26
    Pumpe_oben_an_changetime=27
    Pumpe_unten_an=28
    Pumpe_unten_an_changetime=29
    Pumpe_Brauchwasser_an=30
    Pumpe_Brauchwasser_an_changetime=31
    Brenner_an=32
    Brenner_an_changetime=33
    Brenner_Stoerung=34
    Brenner_Stoerung_changetime=35
    Hand_Dusche=36
    Hand_Dusche_changetime=37
    threadstop=38


##### Start der Idee mit der Idee der Dataclass
@dataclass
class maindata(SensorView, KesselView, ZeitView):
    
    def __init__(self, queue_to_backend:Queue, queue_from_backend:Queue)->None:
        self.queue_to_backend=queue_to_backend
        self.queue_from_backend=queue_from_backend
        
    # Erkenntnis zu dataclass: wenn man einen Defaultvalue für eine Variable vergibt muss man das für alle
    # folgenden Variablen auch machen. Damit nehme ich nun die Werte, die ich in settings.py vergeben habe.
    # Wenn ich die Variablen verwende, dann wird alles ungültig, wenn ich die anderen teile auch für die Datenklasse umbaue.
    # Wenn ich nur die Werte verwende, habe ich sie an mehreren Orten :-( 
    # Fast alle hier gesetzten Werte werden werden beim ersten Lesen aus der DB überschrieben. Damit ist es sowieso egal.
    # Es bleibt aber nicht schön.
    # Wenn ich die Dataclass für alles verwende, dann kann ich die globalen Variablen reduzieren.


    # damit man den thread stoppen kann
    threadstop : bool = False

    #Wartezeit in Sec bevor die nächste Abfrage des WorkdataView durchgeführt wird
    _sleeptime : int = 5

    # wenn Daten geschrieben werden mit dem Lesen warten, damit die Variable nicht
    # überschrieben wird, primitiv, aber hoffentlich ausreichend
    _datawrite: bool = False

    # Defaults werden in settings.py festgelegt ind in dbinit.py als Tabelle angelegt 
    # und von den Werten gesetzt

    # diser Wert wird beim Füllen der Variablen aus der Datenbank zuerst gesetzt
    # er dient als indikator ob sich in der DB etwas geändert hat und ob deswegen alle Variablen neu geladen werden müssen
    # falls er neu gesetzt wird bekommt er den Zeitwert von ViewChanged.
    # Wenn ein Prozess einen Wert in der Tabelle Wordataview ändert, wird der Wert auf den Zeit wert des 
    # veränderten Felds gesetzt
    _lastruntime :int = 0

    # Bei Winter == True haben wir Heizbetrieb
    # Wintertemp ist die Temperatur bei der auf Heizbetrieb geschaltet wird
    _Winter : bool = False
    _Wintertemp: float = 17

    # Kessel ist die aktuelle Kesseltemperatur
    # KesselSoll ist die KesselSolltemperatur
    # KesselMax ist die Temperatur bei der ein Fehler ausgelöst wird
    # Heizen: soll geheizt werden
    # Nachabsenkung: soll die Temperatur Nachts abgesenkt werden?
    # KesselDaten_x und y ist die KesselSollkennlinie
    # die x und y Listen sind die Sensordaten nach x und y gesplittet. 
    # Die Grafikfunktion braucht diese Trennung
    _Kessel : float = 0
    _KesselSoll : float = 0
    _KesselMax : float = 90
    _Heizen : bool = False
    _Nachtabsenkung: bool = False
    _KesselDaten_x : list = field(default_factory=list)
    _KesselDaten_y : list = field(default_factory=list)
    #_KesselIstDaten_x : list = field(default_factory=list)
    #_KesselIstDaten_y : list = field(default_factory=list)


    # Brauchwasser ist die aktuelle Brauchwassertemperatur
    # BrauchwasserSoll ist die Solltemperatur des Brauchwassers
    # BrauchwasserError ist die Temperatur bei der ein Fehler ausgelöst wird
    # BrauchwasserAus ist Wahr wenn kein Brauchwasser erzeugt werden soll.
    _Brauchwasser : float = 0
    #_BrauchwasserDaten_x : list = field(default_factory=list)
    #_BrauchwasserDaten_y : list = field(default_factory=list)
    _BrauchwasserSoll : float = 55
    _BrauchwasserError : float = 70
    _BrauchwasserAus : bool = False
    _Brauchwasserbereiten : bool =False
    _Pumpe_Brauchwasser_an : bool =False
    _Hand_Dusche : bool = False

    # Innen ist die aktuelle Innentemperatur
    _Innen : float = 0
    #_InnenDaten_x : list = field(default_factory=list)
    #_InnenDaten_y : list = field(default_factory=list)
    
    # Innen ist die aktuelle Aussentemperatur
    _Aussen : float = 0 
    #_AussenDaten_x : list = field(default_factory=list)
    #_AussenDaten_y : list = field(default_factory=list)

    # Signalisiert ob die Pumpen an /  aus sind
    _Pumpe_oben_an : bool = False
    _Pumpe_unten_an : bool = False

    # Signalisiert ob der Brenner an ist und ob es eie Störung gibt
    _Brenner_an : bool =False
    _Brenner_Stoerung : bool = False

    # lädt die Daten aus der Datenbank aus der Tabelle WorkDataView 
    # in die klasseninternen Variablen
    def _viewloader(self,initialrun):
        try:
            with sqlite3.connect(settings.DBPATH) as db:
                cursor=db.cursor()
                sql= settings.read_WorkDataView_complete
                cursor.execute(sql)
                results=cursor.fetchone()
                self._lastruntime=(results[dv.ViewChanged.value])

                if initialrun==True:
                    # das läuft nur beim ersten Aufruf um die Variablen mit
                    # DB Inhalt zu zu füllen
                   
                    
                    self._Winter=results[dv.Winter.value]
                    self._Winter_changetime=results[dv.Winter_changetime.value]
                    self._Wintertemp=results[dv.Wintertemp.value]
                    self._Wintertemp_changetime=results[dv.Wintertemp_changetime.value]
                    self._Kessel=results[dv.Kessel.value]
                    self._Kessel_changetime=results[dv.Kessel_changetime.value]
                    self._KesselSoll=results[dv.KesselSoll.value]
                    self._KesselSoll_changetime=results[dv.KesselSoll_changetime.value]
                    self._Heizen=results[dv.Heizen.value]
                    self._Heizen_changetime=results[dv.Heizen_changetime.value]
                    self._Nachtabsenkung=results[dv.Nachtabsenkung.value]
                    self._Nachtabsenkung_changetime=results[dv.Nachtabsenkung_changetime.value]
                    self._Brauchwasser=results[dv.Brauchwasser.value]
                    self._Brauchwasser_changetime=results[dv.Brauchwasser_changetime.value]
                    self._BrauchwasserSoll=results[dv.BrauchwasserSoll.value]
                    self._BrauchwasserSoll_changetime=results[dv.BrauchwasserSoll_changetime.value]
                    self._BrauchwasserAus=results[dv.BrauchwasserAus.value]
                    self._BrauchwasserAus_changetime=results[dv.BrauchwasserAus_changetime.value]
                    self._Brauchwasserbereiten=results[dv.Brauchwasserbereiten.value]
                    self._Brauchwasserbereiten_changetime=results[dv.Brauchwasserbereiten_changetime.value]
                    self._Innen=results[dv.Innen.value]
                    self._Innen_changetime=results[dv.Innen_changetime.value]
                    self._Aussen=results[dv.Aussen.value]
                    self._Aussen_changetime=results[dv.Aussen_changetime.value]
                    self._Pumpe_oben_an=results[dv.Pumpe_oben_an.value]
                    self._Pumpe_oben_an_changetime=results[dv.Pumpe_oben_an_changetime.value]
                    self._Pumpe_unten_an=results[dv.Pumpe_unten_an.value]
                    self._Pumpe_unten_an_changetime=results[dv.Pumpe_unten_an_changetime.value]
                    self._Pumpe_Brauchwasser_an=results[dv.Pumpe_Brauchwasser_an.value]
                    self._Pumpe_Brauchwasser_an_changetime=results[dv.Pumpe_Brauchwasser_an_changetime.value]
                    self._Brenner_an=results[dv.Brenner_an.value]
                    self._Brenner_an_changetime=results[dv.Brenner_an_changetime.value]
                    self._Brenner_Stoerung=results[dv.Brenner_Stoerung.value]
                    self._Brenner_Stoerung_changetime=results[dv.Brenner_Stoerung_changetime.value]
                    self._Hand_Dusche=results[dv.Hand_Dusche.value]
                    self._Hand_Dusche_changetime=results[dv.Hand_Dusche_changetime.value]
                    self.threadstop=results[dv.threadstop.value]
                else:
                    # hier ist die regelmäßige Abfrage der Werte aus der DB weil ViewChanged
                    # sagt, dass es was Neues gibt, jetzt ist nur noch die Frage welche Werte sich
                    # geändert haben
                        
                   
                    if self._Winter_changetime<results[dv.Winter_changetime.value]:
                        self._Winter_changetime=results[dv.Winter_changetime.value]
                        self._Winter=results[dv.Winter.value]

                    if self._Wintertemp_changetime<results[dv.Wintertemp_changetime.value]:
                        self._Wintertemp_changetime=results[dv.Wintertemp_changetime.value]
                        self._Wintertemp=results[dv.Wintertemp.value]

                    if self._Kessel_changetime<results[dv.Kessel_changetime.value]:
                        self._Kessel=results[dv.Kessel.value]
                        self._Kessel_changetime=results[dv.Kessel_changetime.value]
                    
                    if self._KesselSoll_changetime<results[dv.KesselSoll_changetime.value]:
                        self._KesselSoll=results[dv.KesselSoll.value]
                        self._KesselSoll_changetime=results[dv.KesselSoll_changetime.value]
                    
                    if self._Heizen_changetime<results[dv.Heizen_changetime.value]:
                        self._Heizen=results[dv.Heizen.value]
                        self._Heizen_changetime=results[dv.Heizen_changetime.value]
                    
                    if self._Nachtabsenkung_changetime<results[dv.Nachtabsenkung_changetime.value]:
                        self._Nachtabsenkung=results[dv.Nachtabsenkung.value]
                        self._Nachtabsenkung_changetime=results[dv.Nachtabsenkung_changetime.value]
                    
                    if self._Brauchwasser_changetime<results[dv.Brauchwasser_changetime.value]:
                        self._Brauchwasser=results[dv.Brauchwasser.value]
                        self._Brauchwasser_changetime=results[dv.Brauchwasser_changetime.value]
                    
                    if self._BrauchwasserSoll_changetime<results[dv.BrauchwasserSoll_changetime.value]:
                        self._BrauchwasserSoll=results[dv.BrauchwasserSoll.value]
                        self._BrauchwasserSoll_changetime=results[dv.BrauchwasserSoll_changetime.value]
                    
                    if self._BrauchwasserAus_changetime<results[dv.BrauchwasserAus_changetime.value]:
                        self._BrauchwasserAus=results[dv.BrauchwasserAus.value]
                        self._BrauchwasserAus_changetime=results[dv.BrauchwasserAus_changetime.value]
                    
                    if self._Brauchwasserbereiten_changetime<results[dv.Brauchwasserbereiten_changetime.value]:
                        self._Brauchwasserbereiten=results[dv.Brauchwasserbereiten.value]
                        self._Brauchwasserbereiten_changetime=results[dv.Brauchwasserbereiten_changetime.value]
                    
                    if self._Innen_changetime<results[dv.Innen_changetime.value]:
                        self._Innen=results[dv.Innen.value]
                        self._Innen_changetime=results[dv.Innen_changetime.value]

                    if self._Aussen_changetime<results[dv.Aussen_changetime.value]:
                        self._Aussen=results[dv.Aussen.value]
                        self._Aussen_changetime=results[dv.Aussen_changetime.value]
                    
                    if self._Pumpe_oben_an_changetime<results[dv.Pumpe_oben_an_changetime.value]:
                        self._Pumpe_oben_an=results[dv.Pumpe_oben_an.value]
                        self._Pumpe_oben_an_changetime=results[dv.Pumpe_oben_an_changetime.value]
                    
                    if self._Pumpe_unten_an_changetime<results[dv.Pumpe_unten_an_changetime.value]:
                        self._Pumpe_unten_an=results[dv.Pumpe_unten_an.value]
                        self._Pumpe_unten_an_changetime=results[dv.Pumpe_unten_an_changetime.value]
                    
                    if self._Pumpe_Brauchwasser_an_changetime<results[dv.Pumpe_Brauchwasser_an_changetime.value]:
                        self._Pumpe_Brauchwasser_an=results[dv.Pumpe_Brauchwasser_an.value]
                        self._Pumpe_Brauchwasser_an_changetime=results[dv.Pumpe_Brauchwasser_an_changetime.value]
                    
                    if self._Brenner_an_changetime<results[dv.Brenner_an_changetime.value]:
                        self._Brenner_an=results[dv.Brenner_an.value]
                        self._Brenner_an_changetime=results[dv.Brenner_an_changetime.value]
                    
                    if self._Brenner_Stoerung_changetime<results[dv.Brenner_Stoerung_changetime.value]:
                        self._Brenner_Stoerung=results[dv.Brenner_Stoerung.value]
                        self._Brenner_Stoerung_changetime=results[dv.Brenner_Stoerung_changetime.value]
                    
                    if self._Hand_Dusche_changetime<results[dv.Hand_Dusche_changetime.value]:
                        self._Hand_Dusche=results[dv.Hand_Dusche.value]
                        self._Hand_Dusche_changetime=results[dv.Hand_Dusche_changetime.value]
                    
                    self.threadstop=results[dv.threadstop.value]
            cursor.close()
            db.close()
        except sqlite3.Error as e:
            logging.error(f"Error {e} ist aufgetreten")
            exit(1)

    # prüft ob mindestens eine Variable neu aus der DB gelesen werden mmuss, oder nicht
    # True= "neu lesen"
    def _checkview(self)->bool:
        db=sqlite3.connect(settings.DBPATH)
        cursor=db.cursor()
        sql=f"SELECT ViewChanged FROM {settings.WorkDataView} WHERE id=1"
        cursor.execute(sql)
        result=cursor.fetchone()
        cursor.close()
        db.close()
        storetime=result[0]
        if storetime > self._lastruntime:
            return(True)
        else:
            return(False)



    # hier wird regelmäßig die DB abgefragt, damit immer frische Werte vorhanden sind
    # aber wenn gerade geschrieben wird, dann wird eine 1/50 sec gewartet. Vielleicht noch ein wenig viel.
    # schreiben hat Vorrang vor dem Lesen,
    # ein Argument muss man mitgeben...-> dummy
    def _dataviewpolling(self,dummy):
        while (self.threadstop ==False):
            if self._datawrite==False:
                
                self._viewloader(False)
                logging.debug('WorkdataView Pollen')
                time.sleep(self._sleeptime)
            else:
                time.sleep((self._sleeptime)/100)

    
    # hier müssen die aktuellen Werte aus der DB eingelesen werden.
    # da die GUI immer nach dem DB Modul gestartet wird, müssen 
    # hier Werte vorhanden sein. Sind sie es nicht, ist das ein fatler
    # Fehler
    def __post_init__(self):
    
        if checktable(settings.WorkDataView)==False:
            logging.error(f'Die Tabelle {settings.WorkDataView} existiert nicht. Programm wird beendet')
            exit(1) 
        # jetzt die Daten zum ersten Mal aus der DB laden
        # Laden der historischen=letzten Werte der Sensoren (Aussen, Innen,Kessel, Brauchwasser)
        # die Defaults werden dabei überschrieben.
        self._viewloader(True)
        
        # Laden der initialen Kesselkennlinie
        self._kesseldataload()

        # Laden der initialen SensorWerte
        self._sensordataload()

        # Zeitsteuerung laden
        self._zeitsteuerungload()
    
        # starten des Threads für das periodische Update der Dataview-Werte oder Initialisierung
        # ZZ brauche noch einen Ort an dem ich den Thread wieder einfange!
        # vielleicht beim löschen der Klasse?
        dummy=0    

        global dv_poll
        self.dv_poll = threading.Thread(target=self._dataviewpolling, name="Thread-GUI-DataView", args=(dummy,))
        logging.info('Starte DB-Abfrage dataview Thread!')
        settings.ThreadList.append(self.dv_poll)
        self.dv_poll.start()
        logging.debug('DB-Abfrage Thread dataview gestartet!')

        self._start_sensor_thread()
        # jetzt ist alles gestartet 
        self.queue_from_backend.put("WorkDataView_up")
        
    

    # liest einen Eintrag und seine Schreibzeit aus dem WorkDataView
    def _readitem(self,name,namect,value,timestamp):
        db=sqlite3.connect(settings.DBPATH)
        try: 
            
            cursor=db.cursor()
            # t=(name,namect,settings.WorkDataView)
            sql= f"SELECT {name}, {namect} FROM {settings.WorkDataView} WHERE id=1;"
            cursor.execute(sql)
            results=cursor.fetchone()
            storevalue=results[0]
            storetime= results[1]                               
            cursor.close()
            db.close()
            if timestamp < storetime:
                # neue Werte zurückgeben
                return(storevalue,storetime)
            else:
                # alte Werte zurückgeben
                return(value,timestamp)
            
        except sqlite3.Error as e:
            logging.error(f"Der Fehler {e} ist beim Lesen von {name}:{namect} aufgetreten")
            db.close()
            exit(1)


    # scheibt jeden Wert einzeln in die DB zusammen mit den Zeitstempeln
    def _writeitem(self,value,name,namect):
        db=sqlite3.connect(settings.DBPATH)
        try:
            self._datawrite=True
            cursor=db.cursor()
            timestamp=time.time_ns()
            # den neuen Wert und den Time Stamp zwei Mal schreiben damit klar ist, dass sich was geändert hat.
            sql= f"UPDATE {settings.WorkDataView} SET {name}={value},{namect}={timestamp}, \
                 {dv.ViewChanged.name}={timestamp} WHERE id=1"
            cursor.execute(sql)
            db.commit()
            cursor.close()
            self._datawrite=False
            db.close()
            return(timestamp)
        except sqlite3.Error as e:
            logging.error(f"Der Fehler {e} ist beim Schreiben von {name}:{value} aufgetreten")
            db.close()
            exit(1)

    # Thread schliessen wenn Objekt gelöscht wird
    def __del__(self):
        logging.debug('datav Klasse löschen,  Polling DB stop')
        self.threadstop = True
        # wait for Thread to end
        self.dv_poll.join()
        logging.info("datav Klasse gelöscht, Polling gestoppt.")

    # für jede Variable die es benötigt eine "Setter"-funktion erstellen.
    # Denn ein Setzen der Variable soll auch immer den neuen Wert in die DB schreiben.
    # viele Variablen werden nur gelesen. Sie werden durch Sensoren, Oder Regelkreise gesetzt

    @property
    def vWinter(self):
        return self._Winter
    
    @property
    def vWintertemp(self):
        return self._Wintertemp
    
    @vWintertemp.setter
    def vWintertemp(self,value):
        self._Wintertemp=value
        self._writeitem(value,"Wintertemp", "Wintertemp_changetime")   

    @property
    def vKessel(self):
        return self._Kessel
    
    @property
    def vKesselSoll(self):
        return self._KesselSoll
    
    @property
    def vHeizen(self):
        return self._Heizen
    
    @vHeizen.setter
    def vHeizen(self,value):
        # so hier muss das in die DB geschrieben werden
        self._Heizen=value
        self._writeitem(value,"Heizen","Heizen_changetime")  
    
    @property
    def vNachtabsenkung(self):
        return self._Nachtabsenkung
    
    @vNachtabsenkung.setter
    def vNachtabsenkung(self,value):
        # so hier muss das in die DB geschrieben werden
        self._Nachtabsenkung=value
        self._writeitem(value,"Nachtabsenkung","Nachtabsenkung_changetime")  
    
    @property
    def vBrauchwasser(self):
        return self._Brauchwasser

    @property
    def vBrauchwasserSoll(self):
        return self._BrauchwasserSoll
    
    @vBrauchwasserSoll.setter
    def vBrauchwasserSoll(self,value):
        # so hier muss das in die DB geschrieben werden
        self._BrauchwasserSoll=value
        self._writeitem(value,"BrauchwasserSoll","BrauchwasserSoll_changetime")  

    @property
    def vBrauchwasserAus(self):
        return self._BrauchwasserAus
    
    @vBrauchwasserAus.setter
    def vBrauchwasserAus(self,value):
        self._BrauchwasserAus=value
        self._writeitem(value,"BrauchwasserAus","BrauchwasserAus_changetime")
        
    @property
    def vBrauchwasserbereiten(self):
        return self._Brauchwasserbereiten
    
    @vBrauchwasserbereiten.setter
    def vBrauchwasserbereiten(self,value):
        self._Brauchwasserbereiten=value
        self._writeitem(value,"Brauchwasserbereiten","Brauchwasserbereiten_changetime")

    @property
    def vInnen(self):
        return self._Innen
    
    @property
    def vAussen(self):
        return self._Aussen
   
    @property
    def vPumpe_oben_an(self):
        return self._Pumpe_oben_an

    @property
    def vPumpe_unten_an(self):
        return self._Pumpe_unten_an

    @property
    def vPumpe_Brauchwasser_an(self):
        return self._Pumpe_Brauchwasser_an
    
    @property
    def vBrenner_an(self):
        return self._Brenner_an
    
    @vBrenner_an.setter
    def vBrenner_an(self,value):
        # so hier muss das in die DB geschrieben werden
        # aber als zeichenkette. Damit es leichter lesbar ist
        self._Brenner_an=value
        self._writeitem(value,"Brenner_an","Brenner_an_changetime")

    @property
    def vHand_Dusche(self):
        return self._Hand_Dusche
    
    @vHand_Dusche.setter
    def vHand_Dusche(self,value):
        # so hier muss das in die DB geschrieben werden
        # aber als zeichenkette. Damit es leichter lesbar ist
        self._Hand_Dusche=value
        self._Hand_Dusche_changetime=self._writeitem(value,"Hand_Dusche","Hand_Dusche_changetime")

    @property
    def vBrenner_Stoerung(self):
        return self._Brenner_Stoerung
    
    @property
    def vKesselDaten_x(self):
        return self._KesselDaten_x
    
    @property
    def vKesselDaten_y(self):
        return self._KesselDaten_y
    
    @vKesselDaten_y.setter
    def vKesselDaten_y(self,value):
        self._writeKesselDaten_y(value)
