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
#       /threadstop get/post


# import settings
from fastapi import FastAPI,  HTTPException 
from  pydantic import BaseModel
from dataview import datav as datav

class LeseWert(BaseModel):
    Winter:           bool  | None = None 
    Wintertemp:       float | None = None
    Kessel:           float | None = None
    KesselSoll:       float | None = None
    Brauchwasser:     float | None = None
    BrauchwasserSoll: float | None = None
    BrauchwasserAus:  bool  | None = None
    Innen:            float | None = None
    Aussen:           float | None = None
    Pumpe_oben_an:    bool  | None = None
    Pumpe_unten_an:   bool  | None = None
    Pumpe_Brauchwasser_an: bool | None = None
    Brenner_an:       bool  | None = None
    Hand_Dusche:      bool  | None = None
    Brenner_Stoerung: bool  | None = None
    KesselDaten_x:    list[float]| None = None
    KesselDaten_y:    list[float]| None = None
    AussenDaten_x:    list[float]| None = None
    AussenDaten_y:    list[float]| None = None
    InnenDaten_x:     list[float]| None = None
    InnenDaten_y:     list[float]| None = None
    BrauchwasserDaten_x: list[float]| None = None
    BrauchwasserDaten_y: list[float]| None = None
    Zeitsteuerung:       list[str]  | None = None


# Wie heisst die APP für FastAPI
app= FastAPI(title="Heizung")

# was passiert beim Startup der API
# @app.on_event("startup")
# def startup():
#    pass

# was passiert beim Stopen der API
# @app.on_event("shutdown")
# async def shutdown():
#    pass

# http://172.0.0.1/werte/winter:8000


@app.get("/werte/{LeseWert}")
def get_lesewert(LeseWert):
    lw=LeseWert
    result=None
    if lw=="wintertemp":
        result = datav.vWintertemp
    elif lw=="winter":
        result = datav.vWinter
    elif lw=="kessel":    
        result=datav.vKessel
    elif lw=="kesselsoll": 
        print(f"KesselSoll:<{datav.vKesselSoll}>")
        print(type(datav.vKesselSoll))
        result = datav.vKesselSoll,
    elif lw=="brauchwasser":
        result = datav.vBrauchwasser
    elif lw=="brauchwassersoll":
        result=datav.vBrauchwasserSoll
    elif lw=="brauchwasseraus":
        result=datav.vBrauchwasserAus
    elif lw=="innen":
        result=datav.vInnen
    elif lw=="aussen":
        result=datav.vAussen
    elif lw=="pumpeobenan":
        result=datav._Pumpe_oben_an
    elif lw=="pumpeuntenan":
        result=datav._Pumpe_unten_an
    elif lw=="pumpebrauchwasseran":
        result=datav.vPumpe_Brauchwasser_an
    elif lw=="brenneran":
        result=datav.vBrenner_an
    elif lw=="handdusche":
        result=datav.vHand_Dusche
    elif lw=="brennerstoerung":
        result=datav.vBrenner_Stoerung

    elif lw=="kesseldatenx":
        result=datav.vKesselDaten_x
    elif lw=="kesseldateny":
        result=datav.vKesselDaten_y

    elif lw=="aussendatenx":
        result=datav.vAussenDaten_x
    elif lw=="aussendateny":
        result=datav.vAussenDaten_y

    elif lw=="innendatenx":
        result=datav.vInnenDaten_x
    elif lw=="innendateny":
        result=datav.vInnenDaten_y

    elif lw=="brauchwasserdatenx":
        result=datav.vBrauchwasserDaten_x
    elif lw=="brauchwasserdateny":
        result=datav.vBrauchwasserDaten_y

    elif lw=="zeitsteuerung":
        result=datav.vZeitsteuerung
        
    return result

@app.put("/werte/kesselsoll")
async def set_kesselsoll()->int:
    pass
#    return datav.vKesselSoll

@app.put("/werte/brauchwassersoll")
async def set_brauchwassersoll()->int:
    pass
    # return datav.vBrauchwasser

@app.put("/werte/kesseldatenx")
async def set_kesseldatenx():
    pass

@app.put("/werte/kesseldateny")
async def set_kesseldateny():
    pass

@app.put("/werte/threadstop")
async def set_threadstop():
    pass

@app.put("/werte/handdusche")
async def set_handdusche():
    pass

# nicht vergessen! Zum reload nach Codechange!
# uvicorn api:app --reload
# http://127.0.0.1:8000/docs
# http://127.0.0.1:8000/redocs
#
# Openapi Schema
# http://127.0.0.1:8000/openapi.json


    


