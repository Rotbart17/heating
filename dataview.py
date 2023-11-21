#!/usr/bin/env python3
# in diesem Modul wird die Datenaustauschstruktur definiert
# sie versteckt die Datenbankzugriffe in einer Klasse
# so zumindest die Idee!

import settings
from dataclasses import dataclass
import asyncio
import aiosqlite
import logging
from dbinit import checktable



##### Start der Idee mit der Idee  der Dataclass
@dataclass
class data:
    # Defaults werden in settings.py festgelegt ind in dbinit.py als Tabelle angelegt 
    # und von den Werten gesetzt
    
    # Bei Winter == True haben wir Heizbetrieb
    # Wintertemp ist die Temperatur bei der auf Heizbetrieb geschaltet wird
    Winter : bool 
    Wintertemp: float

    # Kessel ist die aktuelle Kesseltemperatur
    # KesselSoll ist die KesselSolltemperatur
    # KesselMax ist die Temperatur bei der ein Fehler ausgelöst wird
    Kessel : float
    KesselSoll : float
    KesselMax : float


    # Brauchwasser ist die aktuelle Brauchwassertemperatur
    # BrauchwasserSoll ist die Solltemperatur des Brauchwassers
    # BrauchwasserError ist die Temperatur bei der ein Fehler ausgelöst wird
    Brauchwasser : float
    BrauchwasserSoll : float
    BrauchwasserError : float
    Pumpe_Brauchwasser_an : bool
    Hand_Dusche : bool = False

    # Innen ist die aktuelle Innentemperatur
    Innen : float
    # Innen ist die aktuelle Aussentemperatur
    Aussen : float

    # Signalisiert ob die Pumpen an /  aus sind
    Pumpe_oben_an : bool 
    Pumpe_unten_an : bool

    # Signalisiert ob der Brenner an ist und ob es eie Störung gibt
    Brenner_an : bool
    Brenner_Stoerung : bool

    
    # lädt die Daten aus der Datenbank in die Variablen
    async def viewloader(self):
        async with aiosqlite.connect(settings.DBPATH) as db:
            sql= f"SELECT * from {settings.WorkDataView} WHERE id =1 ;"
            async with db.execute(sql) as cursor:
                async for results in cursor:
                    self.Winter=results[0][1]
                    self.Wintertemp=results[0][2]
                    self.Kessel=results[0][3]
                    self.KesselSoll=results[0][4]
                    self.Brauchwasser=results[0][5]
                    self.Innen=results[0][6]
                    self.Aussen=results[0][7]
                    self.Pumpe_oben_an=results[0][8]
                    self.Pumpe_unten_an=results[0][9]
                    self.Pumpe_Brauchwasser_an=results[0][10]
                    self.Brenner_an=results[0][11]
                    self.Brenner_Stoerung=results[0][12]
                    self.Hand_Dusche=results[0][13]
        
    
    # hier müssen die aktuellen Werte aus der DB eingelesen werden.
    # da die GUI immer nach dem DB Modul gestartet wird, müssen 
    # hier Werte vorhanden sein. SInd sie es nicht ist das ein fatler
    # Fehler
    def __post_init__():
        if checktable(settings.WorkDataView)==False:
            logging.error(f'Die Tabelle {settings.WorkDataView} ist leer. Programm wird beendet')
            exit(1) 
        # jetzt die Daten aus der DB laden
        data.viewloader()

    # die jeweiligen Werte müssen einzeln in die DB geschrieben werden
    # # InitWorkDataView SQL, schreibt die erste Zeile mit Basiswerten
    # init_WorkDataView_sql = f"INSERT OR REPLACE INTO {WorkDataView} (\
    #                    id, Winter, Wintertemp, Kessel, KesselSoll, Brauchwasser, Innen, Aussen,\
    #                    Pumpe_oben_an, Pumpe_unten_an, Pumpe_Brauchwasser_an, Brenner_an,\
    #                    Brenner_Stoerung, Hand_Dusche ) \
    #                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?);"            

    async def writeitem(self,value,name):
        async with aiosqlite.connect(settings.DBPATH) as db:
            sql= f"INSERT OR REPLACE INTO {settings.WorkDataView} (id,{name}) VALUES (1,{value});"
            async with db.execute(sql):


    # für jede Variable eine "Setter"-funktion.
    # Denn ein Setzen der Variable soll auch immer den neuen Wert in die DB schreiben.
    @property
    def Winter(self):
        return self.Winter
    
    @Winter.setter
    def Winter(self,value):
        # so hier muss das in die DB geschrieben werden
        data.writeitem(value,"Winter")


    @property
    def Wintertemp(self):
        return self.Wintertemp
    
    @Wintertemp.setter
    def Wintertemp(self,value):
        # so hier muss das in die DB geschrieben werden
        data.writeitem(value,"Wintertemp")   

    @property
    def Kessel(self):
        return self.Kessel
    
    @Kessel.setter
    def Kessel(self,value):
        # so hier muss das in die DB geschrieben werden
        data.writeitem(value,"Kessel")    


    @property
    def KesselSoll(self):
        return self.KesselSoll
    
    @KesselSoll.setter
    def KesselSoll(self,value):
        # so hier muss das in die DB geschrieben werden
        data.writeitem(value,"KesselSoll")    


    @property
    def Brauchwasser(self):
        return self.Brauchwasser
    
    @Brauchwasser.setter
    def Brauchwasser(self,value):
        # so hier muss das in die DB geschrieben werden
        data.writeitem(value,"Brauchwasser")  


    @property
    def Innen(self):
        return self.Innen
    
    @Innen.setter
    def Innen(self,value):
        # so hier muss das in die DB geschrieben werden
        data.writeitem(value,"Innen")  

    @property
    def Aussen(self):
        return self.Aussen
    
    @Aussen.setter
    def Aussen(self,value):
        # so hier muss das in die DB geschrieben werden
        data.writeitem(value,"Aussen")  



    @property
    def Pumpe_oben_an(self):
        return self.Pumpe_oben_an
    
    @Pumpe_oben_an.setter
    def Pumpe_oben_an(self,value):
        # so hier muss das in die DB geschrieben werden
        data.writeitem(value,"Pumpe_oben_an")


    @property
    def Pumpe_unten_an(self):
        return self.Pumpe_unten_an
    
    @Pumpe_unten_an.setter
    def Pumpe_unten_an(self,value):
        # so hier muss das in die DB geschrieben werden
        data.writeitem(value,"Pumpe_unten_an")


    @property
    def Pumpe_Brauchwasser_an(self):
        return self.Pumpe_Brauchwasser_an
    
    @Pumpe_Brauchwasser_an.setter
    def Pumpe_Brauchwasser_an(self,value):
        # so hier muss das in die DB geschrieben werden
        data.writeitem(value,"Pumpe_Brauchwasser_an")


    @property
    def Brenner_an(self):
        return self.Brenner_an
    
    @Brenner_an.setter
    def Brenner_an(self,value):
        # so hier muss das in die DB geschrieben werden
        data.writeitem(value,"Brenner_an")


    @property
    def Hand_Dusche(self):
        return self.Hand_Dusche
    
    @Hand_Dusche.setter
    def Hand_Dusche(self,value):
        # so hier muss das in die DB geschrieben werden
        data.writeitem(value,"Hand_Dusche")


    @property
    def Brenner_Stoerung(self):
        return self.Brenner_Stoerung
    
    @Brenner_Stoerung.setter
    def Brenner_Stoerung(self,value):
        # so hier muss das in die DB geschrieben werden
        data.writeitem(value,"Brenner_Stoerung")