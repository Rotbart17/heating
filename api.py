#!/usr/bin/env python3
# in diesem Modul wird die API für die Oberfläche definiert,
# die API kommuniziert mit der Dataclass die wiederum mit der DB 
# man soll ja nich alles als Rootpath machen
# /Werte
#       /Winter
#       /Wintertemp
#       /Kessel
#       /KesselSoll  get/post
#       /Brauchwasser
#       /BrauchwasserSoll get/post
#       /BrauchwasserAus  get/post
#       /Innen
#       /Aussen
#       /Pumpe_oben_an
#       /Pumpe_unten_an
#       /Pumpe_Brauchwasser_an
#       /Brenner_an
#       /Hand_Dusche  get/post
#       /Brenner_Stoerung
#       /KesselDaten_x  get/post
#       /KesselDaten_y  get/post
#       /AussenDaten_x
#       /AussenDaten_y
#       /InnenDaten_x
#       /InnenDaten_y
#       /BrauchwasserDaten_x
#       /BrauchwasserDaten_y
#       /Zeitsteuerung


import settings
from fastapi import FastAPI, UploadFile,APIRouter, Query, HTTPException 
from  pydantic import BaseModel
from dataview import datav as datav

class LeseWert(BaseModel):
    Winter:           int | None = None 
    Wintertemp:       int | None = None
    Kessel:           int | None = None
    KesselSoll:       int | None = None
    Brauchwasser:     int | None = None
    BrauchwasserSoll: int | None = None
    BrauchwasserAus:  int | None = None
    Innen:            int | None = None
    Aussen:           int | None = None
    Pumpe_oben_an:    int | None = None
    Pumpe_unten_an:   int | None = None
    Pumpe_Brauchwasser_an: int | None = None
    Brenner_an:       int | None = None
    Hand_Dusche:      int | None = None
    Brenner_Stoerung: int | None = None
    KesselDaten_x:    list[int]| None = None
    KesselDaten_y:    list[int]| None = None
    AussenDaten_x:    list[int]| None = None
    AussenDaten_y:    list[int]| None = None
    InnenDaten_x:     list[int]| None = None
    InnenDaten_y:     list[int]| None = None
    BrauchwasserDaten_x: list[int]| None = None
    BrauchwasserDaten_y: list[int]| None = None
    Zeitsteuerung:       list[str]| None = None



"""
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
    def vBrauchwasserAus(self):
        return self._BrauchwasserAus
    
    @vBrauchwasserAus.setter
    def vBrauchwasserAus(self,value):
        self._BrauchwasserAus=value
        self._writeitem(value,"BrauchwasserAus","BrauchwasserAus_changetime")


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
    
    @property
    def vZeitsteuerung(self):
        return (self._Zeitsteuerung)

    @vZeitsteuerung.setter
    def vZeitsteuerung(self,value):
        self._zeitsteuerungwrite(value)
 
"""


# Wie heisst die APP für FastAPI
app= FastAPI(title="Heizung")

# was passiert beim Startup der API
# @app.on_event("startup")
def startup():
    pass

# was passiert beim Stopen der API
@app.on_event("shutdown")
async def shutdown():
    pass



# http://172.0.0.1/werte/winter:8000


@app.get("/werte/{LeseWert}")
async def get_lesewert(LeseWert)->int:
    return datav.vWinter

@app.get("/werte/wintertemp")
async def get_wintertemp()->int:
    return datav.vWintertemp

@app.get("/werte/kessel")
async def get_kessel()->int:
    return datav.vKessel

@app.get("/werte/kesselsoll")
async def get_kesselsoll()->int:
    return datav.vKesselSoll

@app.put("/werte/kesselsoll")
async def get_kesselsoll()->int:
    pass
#    return datav.vKesselSoll

@app.get("/werte/brauchwasser")
async def get_brauchwasser()->int:
    return datav.vBrauchwasser

@app.get("/werte/brauchwassersoll")
async def get_brauchwassersoll()->int:
    return datav.vBrauchwasserSoll

@app.put("/werte/brauchwassersoll")
async def get_brauchwassersoll()->int:
    pass
    # return datav.vBrauchwasser


# nicht vergessen! Zum reload nach Codechange!
# uvicorn api:app --reload
# http://127.0.0.1:8000/docs
# http://127.0.0.1:8000/redocs
#
# Openapi Schema
# http://127.0.0.1:8000/openapi.json


    


