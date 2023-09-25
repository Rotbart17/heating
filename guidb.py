#!/usr/bin/env python3
# modul soll den DB Teil für die GUI beinhalten

from databases import Database
import settings
from fastapi import FastAPI, UploadFile,APIRouter, Query, HTTPException 



# hier sind die Inits, die die Basis werte für die Anzeig setzen
async def init_gui_data():
    # Wo ist die DB die Connected wird
    global database
    database = Database(settings.FastApiDBPath)

    await database.connect()
    get_view_data()



# alles beenden...
async def de_init_gui_data():
    global database
    # vielleicht sollte man noch was abspeichern?
    await database.disconnect()


# fetch data for all single values
async def get_view_data():
    sql= f"SELECT * from {settings.WorkDataView} WHERE id =1 ;"
    results = await database.fetch_one(query=sql)
        
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