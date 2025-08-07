import logging
import os
import requests
import pandas as pd
import azure.functions as func
from database import connect_db

def get_liveboard(station="Gent-Sint-Pieters", lang="fr"):
    url = f"https://api.irail.be/liveboard/?station={station}&arrdep=departure&format=json&lang={lang}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    logging.error(f"Erreur API iRail: {response.status_code}")
    return None

# Fonction pour aplatir la liste des départs
def flatten_departures(departures):
    if not departures:
        return []
    df = pd.json_normalize(departures, sep="_")
    return df.to_dict(orient="records")

# Fonction pour insérer les départs dans Azure SQL
def insert_departures(departures):
    print(f"Inserting {len(departures)} departures into the database.")
    # Fix ODBC connection: ensure autocommit and error handling
    conn = connect_db()
    conn.autocommit = True
    cursor = conn.cursor()
    try:
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
        # Insertion des départs (déjà aplatis)
        for dep in departures:
            print(f'Inserting departure: {dep}')
            station = dep.get("station")
            timestamp = dep.get("time")
            vehicle = dep.get("vehicle")
            platform = str(dep.get("platform")) if dep.get("platform") else None
            delay = dep.get("delay", 0)
            cursor.execute(
                "INSERT INTO Departures (station, [time], vehicle, platform, delay) VALUES (?, ?, ?, ?, ?)",
                (station, timestamp, vehicle, platform, delay)
            )
    except Exception as e:
        logging.error(f"ODBC error: {e}")
    finally:
        cursor.close()
        conn.close()

# Azure Functions endpoints
def main(req: func.HttpRequest) -> func.HttpResponse:
    """Endpoint: /api/InsertDepartures - Insert liveboard departures into Azure SQL."""
    station = req.params.get("station") or "Gent-Sint-Pieters"
    data = get_liveboard(station=station)
    if data and "departures" in data:
        departures_raw = data["departures"].get("departure", [])
        departures = flatten_departures(departures_raw)
        insert_departures(departures)
        return func.HttpResponse(
            f"{len(departures)} départs insérés pour {station}.",
            status_code=200
        )
    else:
        return func.HttpResponse("Aucune donnée à insérer.", status_code=200)

def get_liveboard_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Endpoint: /api/GetLiveboard - Get liveboard data from iRail."""
    station = req.params.get("station") or "Gent-Sint-Pieters"
    lang = req.params.get("lang") or "fr"
    data = get_liveboard(station=station, lang=lang)
    if data:
        return func.HttpResponse(json.dumps(data), status_code=200, mimetype="application/json")
    else:
        return func.HttpResponse("Erreur lors de la récupération du liveboard.", status_code=500)

def flatten_departures_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Endpoint: /api/FlattenDepartures - Flatten departures JSON."""
    try:
        departures = req.get_json()
        flat = flatten_departures(departures)
        return func.HttpResponse(json.dumps(flat), status_code=200, mimetype="application/json")
    except Exception as e:
        return func.HttpResponse(f"Erreur: {e}", status_code=400)

def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Endpoint: /api/Health - Health check with Brussels timezone."""
    utc_now = datetime.utcnow()
    brussels_time = utc_now + timedelta(hours=2)  # Summer time
    return func.HttpResponse(
        json.dumps({
            "status": "healthy", 
            "timestamp_utc": utc_now.isoformat(),
            "timestamp_brussels": brussels_time.isoformat(),
            "timezone_note": "Brussels is UTC+2 (summer time)"
        }),
        status_code=200,
        mimetype="application/json"
    )