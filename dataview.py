#!/usr/bin/env python3
# in diesem Modul wird die Datenaustauschstruktur definiert
# sie versteckt die Datenbankzugriffe in einer Klasse
# so zumindest die Idee!

import settings
from dataclasses import dataclass, field
# import asyncio
# import aiosqlite
# from aiosqlite import Error
import logging
from dbinit import checktable
import threading
import time
import sqlite3
from enum import Enum


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
    Brauchwasser=10
    Brauchwasser_changetime=11
    BrauchwasserSoll=12
    BrauchwasserSoll_changetime=13
    Innen=14
    Innen_changetime=15
    Aussen=16
    Aussen_changetime=17
    Pumpe_oben_an=18
    Pumpe_oben_an_changetime=19
    Pumpe_unten_an=20
    Pumpe_unten_an_changetime=21
    Pumpe_Brauchwasser_an=22
    Pumpe_Brauchwasser_an_changetime=23
    Brenner_an=24
    Brenner_an_changetime=25
    Brenner_Stoerung=26
    Brenner_Stoerung_changetime=27
    Hand_Dusche=28
    Hand_Dusche_changetime=29
    threadstop=30

class sens(Enum):
    Kesselsensor=0
    Aussensensor=1
    Innensensor=2
    Brauchwassersensor=3



##### Start der Idee mit der Idee  der Dataclass
@dataclass
class maindata:
    # Erkenntnis zu dataclass: wenn man einen Defaultvalue für eine Variable vergibt muss man das für alle
    # folgenden Variablen auch machen. Damit nehme ich nun die Werte, die ich in settings.py vergeben habe.
    # Wenn ich die Variablen verwende, dann wird alles ungültig, wenn ich die anderen teile auch für die Datenklasse umbaue.
    # Wenn ich nur die Werte verwende, habe ich sie an mehreren Orten :-( 
    # Fast alle hier gesetzten Werte werden werden beim ersten Lesen aus der DB überschrieben. Damit ist es sowieso egal.
    # Es bleibt aber nicht schön.
    # Wenn ich die Dataclass für alles verwende, dann kann ich die globalen Variablen reduzieren.


    # damit man den thread stoppen kann
    threadstop : bool = False

    # Wartezeit in Sec bevor die nächste Abfrage der Sensordaten durchgeführt werden
    _sensorsleeptime : int = 60

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
    # die x und y Listen sind die Sensordaten nach x und y gesplittet. 
    # Die Grafikfunktion braucht diese Trennung
    _Kessel : float = 0
    _KesselSoll : float = 0
    _KesselMax : float = 90
    _KesselDaten_x : list = field(default_factory=list)
    _KesselDaten_y : list = field(default_factory=list)
    _KesselIstDaten_x : list = field(default_factory=list)
    _KesselIstDaten_y : list = field(default_factory=list)


    # Brauchwasser ist die aktuelle Brauchwassertemperatur
    # BrauchwasserSoll ist die Solltemperatur des Brauchwassers
    # BrauchwasserError ist die Temperatur bei der ein Fehler ausgelöst wird
    _Brauchwasser : float = 0
    _BrauchwasserDaten_x : list = field(default_factory=list)
    _BrauchwasserDaten_y : list = field(default_factory=list)
    _BrauchwasserSoll : float = 55
    _BrauchwasserError : float = 70
    _Pumpe_Brauchwasser_an : bool =False
    _Hand_Dusche : bool = False

    # Innen ist die aktuelle Innentemperatur
    _Innen : float = 0
    _InnenDaten_x : list = field(default_factory=list)
    _InnenDaten_y : list = field(default_factory=list)
    # Innen ist die aktuelle Aussentemperatur
    _Aussen : float = 0 
    _AussenDaten_x : list = field(default_factory=list)
    _AussenDaten_y : list = field(default_factory=list)

    # Signalisiert ob die Pumpen an /  aus sind
    _Pumpe_oben_an : bool = False
    _Pumpe_unten_an : bool = False

    # Signalisiert ob der Brenner an ist und ob es eie Störung gibt
    _Brenner_an : bool =False
    _Brenner_Stoerung : bool = False

    # Liste für die Sensoren
    _SensorXListe=[]
    _SensorYListe=[]

     # lädt die Daten aus der Datenbank in die klasseninternen Variablen
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
                    self._KesselSoll_changetime=results[dv.Kessel_changetime.value]
                    self._Brauchwasser=results[dv.Brauchwasser.value]
                    self._Brauchwasser_changetime=results[dv.Brauchwasser_changetime.value]
                    self._BrauchwasserSoll=results[dv.BrauchwasserSoll.value]
                    self._BrauchwasserSoll_changetime=results[dv.Brauchwasser_changetime.value]
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
                    self._Brenner_an_changetime=results[dv.Brenner_Stoerung_changetime.value]
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
                    
                    if self._KesselSoll_changetime<results[dv.Kessel_changetime.value]:
                        self._KesselSoll=results[dv.KesselSoll.value]
                        self._KesselSoll_changetime=results[dv.Kessel_changetime.value]
                    
                    if self._Brauchwasser_changetime<results[dv.Brauchwasser_changetime.value]:
                        self._Brauchwasser=results[dv.Brauchwasser.value]
                        self._Brauchwasser_changetime=results[dv.Brauchwasser_changetime.value]
                    
                    if self._BrauchwasserSoll_changetime<results[dv.Brauchwasser_changetime.value]:
                        self._BrauchwasserSoll=results[dv.BrauchwasserSoll.value]
                        self._BrauchwasserSoll_changetime=results[dv.Brauchwasser_changetime.value]
                    
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
                    
                    if self._Brenner_an_changetime<results[dv.Brenner_Stoerung_changetime.value]:
                        self._Brenner_an=results[dv.Brenner_an.value]
                        self._Brenner_an_changetime=results[dv.Brenner_Stoerung_changetime.value]
                    
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

    # lädt die letzten Werte der Sensoren für die Anzeige
    def _sensordataload(self):
        try:
            with sqlite3.connect(settings.DBPATH) as db:
                cursor=db.cursor()
                # Hier kommt nun eine Schleife über alle Sensoren
                # die in jeder Sensortabelle, die Daten der letzten 24h abfragt
                # diese Datenmenge muss ggf. reduziert werden, da sonst zu viele Messwerte
                # für die Anzeige vorhanden sind. Die Ergebnisse müssen wieder der jeweiligen Liste 
                # zugeordnet werden. Dann kann die Anzeige sie hoffentlich verarbeiten.
                i=0
                for tn in settings.TemperaturSensorList:
                    xl=[]
                    yl=[]
                    sql = f"SELECT begin_date FROM {tn} WHERE begin_date >= datetime('now', '-24 hours');"
                    cursor.execute(sql)
                    results=cursor.fetchall()
                    # Der x-Wert ist die Zeit
                    xl = [item[0] for item in results]
                    self._SensorXListe[i] = xl

                    # Der y-Wert ist die Temperatur
                    sql = f"SELECT value FROM {tn} WHERE begin_date >= datetime('now', '-24 hours');"
                    cursor.execute(sql)
                    results=cursor.fetchall()
                    yl = [item[0] for item in results]
                    self._SensorYListe[i] = yl
                    i+=1
            cursor.close()
            db.close()
        except sqlite3.Error as e:
            logging.error(f"Error {e} ist aufgetreten")
            exit(1)


    # prüft ob mindestens eine Variable neu aus der DB gelesen werden mmuss, oder nicht
    # True= "neu lesen"
    def _checkview(self):
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
                
                self._sensordataload()
                logging.debug('Sensordata Pollen')
                time.sleep(self._sleeptime)
            else:
                time.sleep((self._sleeptime)/100)

    # pollt regelmäßig neue Sensordaten für die Anzeige
    def _sensorpolling(self,dummy):
        while (self.threadstop ==False):
            if self._checkview():
                self._sensordataload()
                logging.debug('WorkdataView Pollen')
                time.sleep(self._sensorsleeptime)
            

    # Laden der Kesselkennlinie
    def _kesseldataload(self):
        try:
            with sqlite3.connect(settings.DBPATH) as db:
                logging.debug('Kesselkennlinie lesen!')
                cursor=db.cursor()
                sql= f"SELECT value_x from {settings.KesselSollTemperatur} ;"
                cursor.execute(sql)
                t=cursor.fetchall()
                self._KesselDaten_x=[item[0] for item in t]
                sql= f"SELECT value_y from {settings.KesselSollTemperatur} ;"
                cursor.execute(sql)
                t=cursor.fetchall()
                cursor.close()
                self._KesselDaten_y=[item[0] for item in t]
            db.close()
        except sqlite3.Error as e:
            logging.error(f"Der Fehler {e} ist beim Lesen der Kesselkennlinie aufgetreten")
            exit(1)


    

    # Speichern der Kesselkennlinie
    # immer die ganze Kennlinie, wird nur beim Ändern der Daten aufgerufen.
    # aber eigentlich muss man die x-Anteile nie schreiben die sind ja fix.
    def _writeKesselDaten_x(self,value):
        self._KesselDaten_x=value.copy()
        try:
            with sqlite3.connect(settings.DBPATH) as db:
                logging.debug('Kesselkennline in DB schreiben!')
                cursor=db.cursor()
                sql= settings.sql_write_KesselKennlinie_x
                i=0
                for _ in range(int(settings.AussenMinTemp),int(settings.AussenMaxTemp),int(settings.AussenTempStep)):
                    t=(i,self._KesselDaten_x[i])
                    cursor.execute(sql,t)
                    i+=1
                cursor.close()
            db.close()
        except sqlite3.Error as e:
            logging.error(f"Der Fehler {e} ist beim Schreiben der Kesselkennlinie_x aufgetreten")
            exit(1)
          

    def _writeKesselDaten_y(self,value):
        self._KesselDaten_y=value.copy()
        try:
            db=sqlite3.connect(settings.DBPATH)
            logging.debug('Kesselkennline in DB schreiben!')
            cursor=db.cursor()
            sql= settings.sql_write_KesselKennlinie_y
            i=1
            for _ in range(int(settings.AussenMinTemp*10),int(settings.AussenMaxTemp*10),int(settings.AussenTempStep*10)):
                t=(self._KesselDaten_y[i-1],i)
                cursor.execute(sql,t)
                i+=1
            db.commit()
            cursor.close()
            db.close()

        except sqlite3.Error as e:
            logging.error(f"Der Fehler {e} ist beim Schreiben der Kesselkennlinie_y aufgetreten")
            exit(1)

    # Daten der Zeitsteuerung laden
    def _zeitsteuerungload(self):
        try:
            with sqlite3.connect(settings.DBPATH) as db:
                logging.debug('Zeitsteuerung lesen!')
                cursor=db.cursor()
                sql= settings.sql_readzeitsteuerung
                cursor.execute(sql)
                t=cursor.fetchall()
                # self._zeitsteuerung=[item[0] for item in t]
                cursor.close()
            db.close()
        except sqlite3.Error as e:
            logging.error(f"Der Fehler {e} ist beim Lesen der Zeitsteuerung aufgetreten")
            exit(1)



    # hier müssen die aktuellen Werte aus der DB eingelesen werden.
    # da die GUI immer nach dem DB Modul gestartet wird, müssen 
    # hier Werte vorhanden sein. Sind sie es nicht, ist das ein fatler
    # Fehler
    def __post_init__(self):
        # damit man die Sensoren in einer Schleife abfragen kann, müssen sie in eine Liste
        # Jason meinte man sollte ien Feld aus Pointern machen. Für C hat er recht.
        # aber so müsste es ja auchgehen.
        self._SensorXListe.append(self._KesselDaten_x)
        self._SensorXListe.append(self._AussenDaten_x)
        self._SensorXListe.append(self._InnenDaten_x)
        self._SensorXListe.append(self._BrauchwasserDaten_x)
        self._SensorYListe.append(self._KesselDaten_y)
        self._SensorYListe.append(self._AussenDaten_y)
        self._SensorYListe.append(self._InnenDaten_y)
        self._SensorYListe.append(self._BrauchwasserDaten_y)

        if checktable(settings.WorkDataView)==False:
            logging.error(f'Die Tabelle {settings.WorkDataView} existiert nicht. Programm wird beendet')
            exit(1) 
        # jetzt die Daten zum ersten Mal aus der DB laden
        # Laden der historischen=letzten Werte der Sensoren (Aussen, Innen,Kessel, Brauchwasser)
        # die Defaults werden dabei überschrieben.
        self._viewloader(True)
        
        # Laden der initialen Kesselkennlinie
        self._kesseldataload()

        # Laden der Initialen SensorWerte
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

        global sensor_poll
        self.sensor_poll = threading.Thread(target=self._sensorpolling, name="Thread-GUI-Sensorpolling", args=(dummy,))
        logging.info('Starte DB-Abfrage Sensor Thread!')
        settings.ThreadList.append(self.sensor_poll)
        self.sensor_poll.start()
        logging.debug('DB-Abfrage Thread Sensor gestartet!')


    # liest einen Eintrag und seine Schreibzeit aus dem WorkDataView
    def _readitem(self,name,namect,value,timestamp):
        try: 
            db=sqlite3.connect(settings.DBPATH)
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
            logging.error(f"Der Fehler {e} ist beim Schreiben von {name}:{value} aufgetreten")
            db.close()
            exit(1)


    # scheibt jeden Wert einzeln in die DB zusammen mit den Zeitstempeln
    def _writeitem(self,value,name,namect):
        try:
            self._datawrite=True
            db=sqlite3.connect(settings.DBPATH)
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
    # viele Variablen werden nur gelesen. Sie weren durch Sensoren, Oder Regelkreise gesetzt

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

    @property
    def vKesselIstDaten_x(self):
        return self._SensorXListe[sens.Kesselsensor.value]

    @property
    def vKesselIstDaten_y(self):
        return self._SensorYListe[sens.Kesselsensor.value]

    @property
    def vAussenDaten_x(self):
        return self._SensorXListe[sens.Aussensensor.value]

    @property
    def vAussenDaten_y(self):
        return self._SensorYListe[sens.Aussensensor.value]

    @property
    def vInnenDaten_x(self):
        return self._SensorXListe[sens.Innensensor.value]

    @property
    def vInnenDaten_y(self):
        return self._SensorYListe[sens.Innensensor.value]
    
    @property
    def vBrauchwasserDaten_x(self):
        return self._SensorXListe[sens.Brauchwassersensor.value]

    @property
    def vBrauchwasserDaten_y(self):
        return self._SensorYListe[sens.Brauchwassersensor.value]
    
# es ist schon Mist die Klasse durch den Import in gui.py global zu definieren!
# da hätte ich gerne einen besseren Ort   
datav=maindata()