# Zum Test erstmal ein Beispiel aus Stackoverflow
# das muss ersetzt werden mit 
# der Abfrage der Tabelle für die Anzeige der Einzelwerte
# Setzen der Einzelwerte
# der Abfrage der Wertepaare für die Grafiken der Sensoren 


import settings
from fastapi import FastAPI, UploadFile,APIRouter, Query, HTTPException 
from fastapi.middleware.cors import CORSMiddleware
from databases import Database
from nicegui import ui

# Wo ist die DB die Connected wird
database = Database("sqlite:///heizung.db")
# Wie heisst die APP für FastAPI
app= FastAPI(title="Heizung")

@app.on_event("startup")
async def database_connect():
    await database.connect()


@app.on_event("shutdown")
async def database_disconnect():
    await database.disconnect()


# http://172.0.0.1:8000/test/1

@app.get("/test/{id}")
async def fetch_data(id: int):
    query = "SELECT * FROM Kesselsensor WHERE id={}".format(int(str(id)))
    results = await database.fetch_all(query=query)
    return results

@app.get("/getdata")
async def fetch_view_data():
    global results
    sql= f"SELECT * from {settings.WorkDataView} ;"
    results = await database.fetch_all(query=sql)
    if not results:
        raise HTTPException(status_code=404, detail=f"Keine Daten vorhanden!")
    return results


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


