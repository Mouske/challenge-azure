import logging
import os
import requests
import pyodbc
import pandas as pd
import azure.functions as func
from database import connect_db

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

def get_data_from_irail(endpoint, params):
    base_url = "https://api.irail.be"
    url = f"{base_url}/{endpoint}"
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    logging.error(f"Erreur API iRail: {response.status_code} sur {url}")
    return None

def flatten_departures(departures):
    if not departures:
        return []
    df = pd.json_normalize(departures, sep="_")
    return df.to_dict(orient="records")

def insert_departures(departures):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Departures' AND xtype='U')
        CREATE TABLE Departures (
            id INT IDENTITY(1,1) PRIMARY KEY,
            station NVARCHAR(255),
            [time] BIGINT,
            vehicle NVARCHAR(100),
            platform NVARCHAR(50),
            delay INT
        )
    """)
    conn.commit()
    for dep in departures:
        station = dep.get("station")
        timestamp = dep.get("time")
        vehicle = dep.get("vehicle")
        platform = str(dep.get("platform")) if dep.get("platform") else None
        delay = dep.get("delay", 0)
        cursor.execute(
            "INSERT INTO Departures (station, [time], vehicle, platform, delay) VALUES (?, ?, ?, ?, ?)",
            (station, timestamp, vehicle, platform, delay)
        )
    conn.commit()
    cursor.close()
    conn.close()

# Route 1 : Liveboard (départs)
@app.route(route="liveboard")
def liveboard(req: func.HttpRequest) -> func.HttpResponse:
    station = req.params.get("station") or "Gent-Sint-Pieters"
    data = get_data_from_irail("liveboard", {
        "station": station,
        "arrdep": "departure",
        "format": "json",
        "lang": "fr"
    })
    if data and "departures" in data:
        departures_raw = data["departures"].get("departure", [])
        departures = flatten_departures(departures_raw)
        insert_departures(departures)
        return func.HttpResponse(f"{len(departures)} départs insérés pour {station}.", status_code=200)
    return func.HttpResponse("Aucune donnée à insérer.", status_code=200)

# Route 2 : Connections (exemple)
@app.route(route="connections")
def connections(req: func.HttpRequest) -> func.HttpResponse:
    from_station = req.params.get("from") or "Gent-Sint-Pieters"
    to_station = req.params.get("to") or "Brussels-Central"
    data = get_data_from_irail("connections", {
        "from": from_station,
        "to": to_station,
        "format": "json",
        "lang": "fr"
    })
    # Tu peux adapter ici l’insertion selon le format renvoyé par connections
    if data and "connection" in data:
        # Traitement et insertion éventuelle ici
        return func.HttpResponse(f"Connections entre {from_station} et {to_station} récupérées.", status_code=200)
    return func.HttpResponse("Aucune donnée à insérer.", status_code=200)

# Route 3 : Exemple route delay (à adapter selon les données disponibles)
@app.route(route="delays")
def delays(req: func.HttpRequest) -> func.HttpResponse:
    station = req.params.get("station") or "Gent-Sint-Pieters"
    data = get_data_from_irail("liveboard", {
        "station": station,
        "arrdep": "departure",
        "format": "json",
        "lang": "fr"
    })
    if data and "departures" in data:
        departures_raw = data["departures"].get("departure", [])

        def to_int(val):
            try:
                return int(val)
            except (TypeError, ValueError):
                return 0

        delayed = [d for d in departures_raw if to_int(d.get("delay", 0)) > 0]
        departures = flatten_departures(delayed)
        insert_departures(departures)
        return func.HttpResponse(f"{len(departures)} départs en retard insérés pour {station}.", status_code=200)
    return func.HttpResponse("Aucune donnée à insérer.", status_code=200)

