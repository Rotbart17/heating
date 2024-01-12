#!/usr/bin/env python3
# in diesem Modul wird die Datenaustauschstruktur definiert
# sie versteckt die Datenbankzugriffe in einer Klasse
# so zumindest die Idee!

import settings
from dataclasses import dataclass, field
# import asyncio
# import aiosqlite
from aiosqlite import Error
import logging
from dbinit import checktable
import threading
import time
import sqlite3

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

    #Wartezeit in Sec bevor die nächste Abfrage des WorkdataView durchgeführt wird
    sleeptime : int = 5

    # wenn daten geschrieben werden mit dem lesen warten, damit die Variable nicht
    # überschrieben wird
    datawrite: bool = False

    # Defaults werden in settings.py festgelegt ind in dbinit.py als Tabelle angelegt 
    # und von den Werten gesetzt
    
    # Bei Winter == True haben wir Heizbetrieb
    # Wintertemp ist die Temperatur bei der auf Heizbetrieb geschaltet wird
    _Winter : bool = False
    _Wintertemp: float = 17

    # Kessel ist die aktuelle Kesseltemperatur
    # KesselSoll ist die KesselSolltemperatur
    # KesselMax ist die Temperatur bei der ein Fehler ausgelöst wird
    _Kessel : float = 0
    _KesselSoll : float = 0
    _KesselMax : float = 90
    _KesselDaten_x : list = field(default_factory=list)
    _KesselDaten_y : list = field(default_factory=list)
  

    # Brauchwasser ist die aktuelle Brauchwassertemperatur
    # BrauchwasserSoll ist die Solltemperatur des Brauchwassers
    # BrauchwasserError ist die Temperatur bei der ein Fehler ausgelöst wird
    _Brauchwasser : float = 0
    _BrauchwasserSoll : float = 55
    _BrauchwasserError : float = 70
    _Pumpe_Brauchwasser_an : bool =False
    _Hand_Dusche : bool = False

    # Innen ist die aktuelle Innentemperatur
    _Innen : float = 0
    # Innen ist die aktuelle Aussentemperatur
    _Aussen : float = 0 

    # Signalisiert ob die Pumpen an /  aus sind
    _Pumpe_oben_an : bool = False
    _Pumpe_unten_an : bool = False

    # Signalisiert ob der Brenner an ist und ob es eie Störung gibt
    _Brenner_an : bool =False
    _Brenner_Stoerung : bool = False

     # lädt die Daten aus der Datenbank in die klasseninternen Variablen
    def viewloader(self):
        try:
            with sqlite3.connect(settings.DBPATH) as db:
                cursor=db.cursor()
                sql= f"SELECT * from {settings.WorkDataView} WHERE id =1 ;"
                cursor.execute(sql)
                results=cursor.fetchone()
                self._Winter=str2bool(results[1])
                self._Wintertemp=results[2]
                self._Kessel=results[3]
                self._KesselSoll=results[4]
                self._Brauchwasser=results[5]
                self._BrauchwasserSoll=results[6]
                self._Innen=results[7]
                self._Aussen=results[8]
                self._Pumpe_oben_an=str2bool(results[9])
                self._Pumpe_unten_an=str2bool(results[10])
                self._Pumpe_Brauchwasser_an=str2bool(results[11])
                self._Brenner_an=str2bool(results[12])
                self._Brenner_Stoerung=str2bool(results[13])
                self._Hand_Dusche=str2bool(results[14])
                self.threadstop=str2bool(results[15])
            cursor.close()
            db.close()
        except sqlite3.Error as e:
            logging.error(f"Error {e} ist aufgetreten")
            exit(1)



    # hier wird regelmäßig die DB abgefragt, damit immer frische Werte vorhanden sind
    # aber wenn gerade geschrieben wird, dann wird eine 1/50 sec gewartet. Vielleicht noch ein wenig viel.
    # schreiben hat Vorrang vor dem Lesen,
    # ein Argument muss man mitgeben...-> dummy

    def dbpolling(self,dummy):
        while (self.threadstop ==False):
            if self.datawrite==False:
                self.viewloader()
                logging.debug('WorkdataView Pollen')
                time.sleep(self.sleeptime)
            else:
                time.sleep(0.05)

    # Laden der Kesselkennlinie
    def kesseldataload(self):
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
    def writeKesselDaten_x(self,value):
        self._KesselDaten_x=value.copy()
        try:
            with sqlite3.connect(settings.DBPATH) as db:
                logging.debug('Kesselkennline in DB schreiben!')
                cursor=db.cursor()
                sql= settings.sql_write_KesselKennlinie_x
                i=0
                for _ in range(settings.KesselMinTemp,settings.KesselMaxTemp,settings.KesselTempStep):
                    t=(i,self._KesselDaten_x[i])
                    cursor.execute(sql,t)
                    i+=1
                cursor.close()
            db.close()
        except sqlite3.Error as e:
            logging.error(f"Der Fehler {e} ist beim Schreiben der Kesselkennlinie_x aufgetreten")
            exit(1)
          

    def writeKesselDaten_y(self,value):
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
    
    # hier müssen die aktuellen Werte aus der DB eingelesen werden.
    # da die GUI immer nach dem DB Modul gestartet wird, müssen 
    # hier Werte vorhanden sein. Sind sie es nicht, ist das ein fatler
    # Fehler
    def __post_init__(self):
        if checktable(settings.WorkDataView)==False:
            logging.error(f'Die Tabelle {settings.WorkDataView} ist leer. Programm wird beendet')
            exit(1) 
        # jetzt die Daten zum ersten Mal aus der DB laden
        # Laden der historischen=letzten Werte der Sensoren (Aussen, Innen,Kessel, Brauchwasser)
        # die Defaults werden dabei überschrieben.
        self.viewloader()
        
        # Laden der Kesselkennlinie
        self.kesseldataload()
    
        # starten der Threads für das periodische Update der Werte oder Initialisierung
        # ZZ brauche noch einen Ort an dem ich den Thread wieder einfange!
        # vielleicht beim löschen der Klasse?
        dummy=0    
        global x
        self.x = threading.Thread(target=self.dbpolling, name="Thread-GUIDB-Abfrage", args=(dummy,))
        
        logging.info('Starte DB-Abfrage Thread!')
        settings.ThreadList.append(self.x)
        self.x.start()
        logging.debug('DB-Abfrage Thread gestartet!')

     

    # scheibt jeden Wert einzeln in die DB
    def writeitem(self,value,name):
        try:
            db=sqlite3.connect(settings.DBPATH)
            cursor=db.cursor()
            t=(name,value)
            sql= settings.write_Workdataview_value
            self.writeitem=True
            cursor.execute(sql,t)
            self.writeitem=False
            cursor.commit()
            cursor.close()
            db.close()
        except sqlite3.Error as e:
            logging.error(f"Der Fehler {e} ist beim Schreiben von {name}:{value} aufgetreten")
            db.close()
            exit(1)

    # Thread schliessen wenn Objekt gelöscht wird
    def __del__(self):
        logging.debug('datav Klasse löschen,  Polling DB stop')
        self.threadstop = True
        # wait for Thread to end
        self.x.join()
        logging.info("datav Klasse gelöscht, Polling gestoppt.")

    # für jede Variable die es benötigt eine "Setter"-funktion erstellen.
    # Denn ein Setzen der Variable soll auch immer den neuen Wert in die DB schreiben.
    # viele Variablen werden nur gelesen. Sie weren durch Sensoren, Oder Regelkreise gesetzt

    @property
    def Winter(self):
        return self._Winter
    
    @property
    def Wintertemp(self):
        return self._Wintertemp
    
    @Wintertemp.setter
    def Wintertemp(self,value):
        # so hier muss das in die DB geschrieben werden
        type(maindata).writeitem(value,"Wintertemp")   

    @property
    def Kessel(self):
        return self._Kessel
    
    @property
    def KesselSoll(self):
        return self._KesselSoll
    
    @property
    def Brauchwasser(self):
        return self._Brauchwasser

    @property
    def BrauchwasserSoll(self):
        return self._BrauchwasserSoll
    
    @BrauchwasserSoll.setter
    def BrauchwasserSoll(self,value):
        # so hier muss das in die DB geschrieben werden
        self.writeitem(value,"BrauchwasserSoll")  

    @property
    def Innen(self):
        return self._Innen
    
    @property
    def Aussen(self):
        return self._Aussen
   
    @property
    def Pumpe_oben_an(self):
        return self._Pumpe_oben_an

    @property
    def Pumpe_unten_an(self):
        return self._Pumpe_unten_an

    @property
    def Pumpe_Brauchwasser_an(self):
        return self._Pumpe_Brauchwasser_an
    
    @property
    def Brenner_an(self):
        return self._Brenner_an
    
    @Brenner_an.setter
    def Brenner_an(self,value):
        # so hier muss das in die DB geschrieben werden
        self.writeitem(str(value),"Brenner_an")

    @property
    def Hand_Dusche(self):
        return self._Hand_Dusche
    
    @Hand_Dusche.setter
    def Hand_Dusche(self,value):
        # so hier muss das in die DB geschrieben werden
        self.writeitem(str(value),"Hand_Dusche")

    @property
    def Brenner_Stoerung(self):
        return self._Brenner_Stoerung
    
    @property
    def KesselDaten_x(self):
        return self._KesselDaten_x
    
    # @KesselDaten_x.setter
    # def KesselDaten_x(self,value):
    #    self.writeKesselDaten_x(value)

    @property
    def KesselDaten_y(self):
        return self._KesselDaten_y
    
    @KesselDaten_y.setter
    def KesselDaten_y(self,value):
        self.writeKesselDaten_y(value)



# es ist schon Mist die Klasse durch den Import in gui.py global zu definieren!
# da hätte ich gerne einen besseren Ort   
datav=maindata()