#!/usr/bin/env python3
# in diesem Modul wird die Datenaustauschstruktur definiert
# sie versteckt die Datenbankzugriffe in einer Klasse
# so zumindest die Idee!

import settings
from dataclasses import dataclass, field
import asyncio
# from sqlite3 import Error
import aiosqlite
from aiosqlite import Error
import logging
from dbinit import checktable
import threading
import datetime




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

    #Wartezeit bevor die nächste Abfrage des WorkdataView durchgeführt wird
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


# db = await aiosqlite.connect(...)
# cursor = await db.execute('SELECT * FROM some_table')
#row = await cursor.fetchone()
#rows = await cursor.fetchall()
#await cursor.close()
# await db.close()

    
    # lädt die Daten aus der Datenbank in die Variablen
    def viewloader(self):
        try:    
            db = aiosqlite.connect(settings.DBPATH)
        except Error as e:
            logging.error('Die Datenbank konnte nicht geöffnet werden. Programm wird beendet. {e}')
            exit(1)
        try:    
            sql= f"SELECT * from {settings.WorkDataView} WHERE id=1;"
            cursor = db.execute(sql)
            results = cursor.fetchone()
            self._Winter=results[0][1]
            self._Wintertemp=results[0][2]
            self._Kessel=results[0][3]
            self._KesselSoll=results[0][4]
            self._Brauchwasser=results[0][5]
            self._BrauchwasserSoll=results[0][6]
            self._Innen=results[0][7]
            self._Aussen=results[0][8]
            self._Pumpe_oben_an=results[0][9]
            self._Pumpe_unten_an=results[0][10]
            self._Pumpe_Brauchwasser_an=results[0][11]
            self._Brenner_an=results[0][12]
            self._Brenner_Stoerung=results[0][13]
            self._Hand_Dusche=results[0][14]
            self.threadstop=results[0][15]
            cursor.close()
        except KeyError:
            logging.error('Die Datenbank konnte nicht abgefragt werden. Programm wird beendet')
            exit(1)

    # hier wird regelmäßig die DB abgefragt, damit immer frische Werte vorhanden sind
    # aber wenn gerade geschrieben wird, dann wird eine 1/50 sec gewartet. Vielleicht noch ein wenig viel.
    # schreiben hat Vorrang vor dem Lesen

    async def dbpolling(self):
        while (self.threadstop ==False):
            if self.datawrite==False:
                self.viewloader()
                logging.debug('WorkdataView Pollen')
                asyncio.sleep(self.sleeptime)
            else:
                asyncio.sleep(0.05)

    # Laden der Kesselkennlinie
    async def kesseldataload(self):
        async with aiosqlite.connect(settings.DBPATH) as db:
            logging.debug('Kesselkennlinie lesen!')
            sql= f"SELECT value_x from {settings.KesselSollTemperatur} ;"
            async with db.execute(sql) as cursor:
                self._KesselDaten_x=await cursor.fetchall()

            sql= f"SELECT value_y from {settings.KesselSollTemperatur} ;"
            async with db.execute(sql) as cursor:
                self._KesselDaten_y=await cursor.fetchall()

    # Speichern der Kesselkennlinie
    # immer die ganze Kennlinie, wird nur beim Ändern der Daten aufgerufen.
    async def kesseldatasave(self):
        async with aiosqlite.connect(settings.DBPATH) as db:
            logging.debug('Kesselkennline in DB schreiben!')
            sql= settings.sql_init_Kesselkennlinie
            i=0
            for _ in range(settings.KesselMinTemp,settings.KesselMaxTemp,settings.KesselTempStep):
                await db.execute(sql,self.KesselDaten_x[i], self.KesselDaten_y[i])
                i+=1
            

    
    # hier müssen die aktuellen Werte aus der DB eingelesen werden.
    # da die GUI immer nach dem DB Modul gestartet wird, müssen 
    # hier Werte vorhanden sein. Sind sie es nicht, ist das ein fatler
    # Fehler
    def __post_init__(self):
        if checktable(settings.WorkDataView)==False:
            logging.error(f'Die Tabelle {settings.WorkDataView} ist leer. Programm wird beendet')
            exit(1) 
        # jetzt die Daten zum ersten Mal aus der DB laden
        # Laden der historischen Werte der Sensoren (Aussen, Innen,Kessel, Brauchwasser)
        self.viewloader()
        # Laden der Kesselkennlinie
        self.kesseldataload()
    
        # starten der Threads für das periodische Update der Werte oder Initialisierung
            
        self.x = threading.Thread(target=self.dbpolling, name="Thread-GUI-DB-Abfrage", args=(self,))
        logging.info('Starte DB-abfrage Thread!')
        settings.ThreadList.append(self.x)
        self.x.start()
        logging.debug('DB-Abfrage Thread gestartet!')



    # die jeweiligen Werte müssen einzeln in die DB geschrieben werden
    # # InitWorkDataView SQL, schreibt die erste Zeile mit Basiswerten
    # init_WorkDataView_sql = f"INSERT OR REPLACE INTO {WorkDataView} (\
    #                    id, Winter, Wintertemp, Kessel, KesselSoll, Brauchwasser, Innen, Aussen,\
    #                    Pumpe_oben_an, Pumpe_unten_an, Pumpe_Brauchwasser_an, Brenner_an,\
    #                    Brenner_Stoerung, Hand_Dusche ) \
    #                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?);"            

    # scheibt jeden Wert einzeln
    async def writeitem(self,value,name):
        async with aiosqlite.connect(settings.DBPATH) as db:
            sql= f"INSERT OR REPLACE INTO {settings.WorkDataView} (id,{name}) VALUES (1,{value});"
            self.writeitem=True
            async with db.execute(sql):
                pass
            self.writeitem=False


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
        self.writeitem(value,"Wintertemp")   

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
        self.writeitem(value,"Brenner_an")

    @property
    def Hand_Dusche(self):
        return self._Hand_Dusche
    
    @Hand_Dusche.setter
    def Hand_Dusche(self,value):
        # so hier muss das in die DB geschrieben werden
        self._Hand_Dusche=value
        self.writeitem(value,"Hand_Dusche")

    @property
    def Brenner_Stoerung(self):
        return self._Brenner_Stoerung
    
    @property
    def KesselDaten_x(self):
        return self._KesselDaten_x
    
    @KesselDaten_x.setter
    def KesselDaten_x(self,value):
        self._KesselDaten_x=value
        # so hier muss das in die DB geschrieben werden
        self.writeitem(value,"KesselDaten_x)")
    
    @property
    def KesselDaten_y(self):
        return self._KesselDaten_y
    
    @KesselDaten_y.setter
    def KesselDaten_y(self,value):
        self._KesselDaten_y=value
        # so hier muss das in die DB geschrieben werden
        self.writeitem(value,"KesselDaten_y)")        
