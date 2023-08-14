#!/usr/bin/env python3
# in diesem Modul wird die API für die Oberfläche definiert,

import settings
from fastapi import FastAPI, UploadFile,APIRouter, Query, HTTPException 
# from fastapi.middleware.cors import CORSMiddleware
from databases import Database


# Wo ist die DB die Connected wird
database = Database("sqlite:///heizung.db")
# Wie heisst die APP für FastAPI
app= FastAPI(title="Heizung")

# was passiert beim Startup der API
@app.on_event("startup")
async def database_connect():
    await database.connect()

# was passiert beim Stopen der API
@app.on_event("shutdown")
async def database_disconnect():
    await database.disconnect()



# http://172.0.0.1:8000/test/1

@app.get("/test/{id}")
async def fetch_data(id: int):
    query = "SELECT * FROM Kesselsensor WHERE id={}".format(int(str(id)))
    results = await database.fetch_all(query=query)
    return results

# holt alle Std-Daten für die Anzeige
@app.get("/getviewdata")
async def fetch_view_data():
    global results
    sql= f"SELECT * from {settings.WorkDataView} ;"
    results = await database.fetch_all(query=sql)
    if not results:
        raise HTTPException(status_code=404, detail=f"Keine Daten vorhanden!")
    return results

# holt alle Daten für Kesselkennliniengrafik
@app.get("/gettankdataset")
async def fetch_tank_dataset():
    global results
    sql= f"SELECT * from {settings.KesselSollTemperatur} ;"
    results = await database.fetch_all(query=sql)
    if not results:
        raise HTTPException(status_code=404, detail=f"Keine Daten vorhanden!")
    return results



# holt alle Daten für Brauchwassergrafik
# holt alle Daten für Kesselgrafik
# holt alle Daten für Innen-grafik
# holt alle Daten für Aussengrafik

# Schreibt alle Daten für Kesselkennliniengrafik
# Schreibt Wintertemp
# Schreibt Brauchwassertemp
# holt Loginfo
# löscht Fehlerstatus



# wir brauchen für diese Daten Lese und Schreibfunktionen
# Winter= True
# Wintertemp=17
# Kessel = 0
# ErrorKessel= 90
# Brauchwasser = 0
# Innen = 0
# Aussen = 0
# Pumpe_oben_an = False
# Pumpe_unten_an = False
# Pumpe_Brauchwasser_an = False
# Brenner_an = False
# Brenner_Stoerung = False
# Hand_Dusche = False





# nicht vergessen! Zum reload nach Codechange!
# uvicorn api:app --reload
# http://127.0.0.1:8000/docs
# http://127.0.0.1:8000/redocs
#
# Openapi Schema
# http://127.0.0.1:8000/openapi.json





# with ui.row():
#    ui.label('Aussen').style('color: #888; font-weight: bold')
#    ui.label(results[Aussen]).style('color: #888; font-weight: bold')
    


# ui.run()


