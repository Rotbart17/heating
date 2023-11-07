#!/usr/bin/env python3
# in diesem Modul wird die API für die Oberfläche definiert,

import settings
from fastapi import FastAPI, UploadFile,APIRouter, Query, HTTPException 
# from fastapi.middleware.cors import CORSMiddleware
# from databases import Database
import aiosqlite
# import sqlite3
import asyncio


# Wo ist die DB die Connected wird
# database = Database("sqlite:///heizung.db")

# Wie heisst die APP für FastAPI
app= FastAPI(title="Heizung")


# was passiert beim Startup der API
# @app.on_event("startup")
def startup():
    pass
    # global database
    # database = aiosqlite.connect(settings.DBPATH)
    # async def database_connect():
    #    await database.connect()

# was passiert beim Stopen der API
@app.on_event("shutdown")
async def shutdown():
    await database.close()
    # async def database_disconnect():
    #    await database.disconnect()



# http://172.0.0.1:8000/test/1

# nur Spielkram zum experimentieren
@app.get("/test/{id}")
async def fetch_data(id: int):
    database = await aiosqlite.connect(settings.DBPATH)
    sql = "SELECT * FROM Kesselsensor WHERE id={}".format(int(str(id)))
    cursor = await database.execute(sql)
    result= await cursor.fetchall()
    return result

# holt alle Std-Daten für die Anzeige
@app.get("/getviewdata")
async def get_view_data():
    database = await aiosqlite.connect(settings.DBPATH)
    sql= f"SELECT * from {settings.WorkDataView} WHERE id=1;"
    cursor = await database.execute(sql)
    results = await cursor.fetchall()
        
    if not results:
        raise HTTPException(status_code=404, detail=f"Keine Daten vorhanden!")
    settings.Winter=results[0][1]
    settings.Wintertemp=results[0][2]
    settings.Kessel=results[0][3]
    settings.KesselSoll=results[0][4]
    settings.Brauchwasser=results[0][5]
    settings.Innen=results[0][6]
    settings.Aussen=results[0][7]
    settings.Pumpe_oben_an=results[0][8]
    settings.Pumpe_unten_an=results[0][9]
    settings.Pumpe_Brauchwasser_an=results[0][10]
    settings.Brenner_an=results[0][11]
    settings.Brenner_Stoerung=results[0][12]
    settings.Hand_Dusche=results[0][13]
    
    return results

# holt alle x Daten für Kesselkennliniengrafik
# @app.get("/gettankdatasetx")
async def get_tank_dataset_x():
    sql= f"SELECT value_x from {settings.KesselSollTemperatur} ;"
    cursor= await database.execute(sql)
    results = cursor.fetch_all()
    if not results:
        raise HTTPException(status_code=404, detail=f"Keine Daten vorhanden!")
    settings.tankdataset_x=results
    print(settings.tankdataset_x)
    return results

# holt alle y Daten für Kesselkennliniengrafik
# @app.get("/gettankdatasety")
async def get_tank_dataset_y():
    sql= f"SELECT value_y from {settings.KesselSollTemperatur} ;"
    cursor= await database.execute(sql)
    results = await cursor.fetch_all()
    if not results:
        raise HTTPException(status_code=404, detail=f"Keine Daten vorhanden!")
    settings.tankdataset_y=results
    # print(settings.tankdataset_y)
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
    
def main():
    startup()
    asyncio.run(get_view_data())
    get_tank_dataset_x()
    get_tank_dataset_y()


# ui.run()
if __name__ == '__main__':
    
    main()
    print("Ende!")
    


