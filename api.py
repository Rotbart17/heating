# Zum Test erstmal ein Beispiel aus Stackoverflow
# das muss ersetzt werden mit 
# der Abfrage der Tabelle für die Anzeige der Einzelwerte
# Setzen der Einzelwerte
# der Abfrage der Wertepaare für die Grafiken der Sensoren 



from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from databases import Database

database = Database("sqlite:///heizung.db")
app= FastAPI()

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

    return  results

# nicht vergessen! Zum reload nach Codechange!
# uvicorn api:app --reload
# http://127.0.0.1:8000/docs
# http://127.0.0.1:8000/redocs
#
# OPenapi Schema
# http://127.0.0.1:8000/openapi.json
