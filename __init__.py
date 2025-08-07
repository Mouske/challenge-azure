import logging
import os
import requests
import pyodbc
import azure.functions as func
from database import connect_db

# Fonction pour récupérer le liveboard depuis iRail
def get_liveboard(station="Gent-Sint-Pieters", lang="fr"):
    url = f"https://api.irail.be/liveboard/?station={station}&arrdep=departure&format=json&lang={lang}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    logging.error(f"Erreur API iRail: {response.status_code}")
    return None

# Fonction pour insérer les départs dans Azure SQL
def insert_departures(departures):
    conn = connect_db()
    cursor = conn.cursor()

    # Création de la table si elle n'existe pas
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

    # Insertion des départs
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

# Fonction principale appelée par Azure Functions
def main(req: func.HttpRequest) -> func.HttpResponse:
    station = req.params.get("station") or "Gent-Sint-Pieters"
    data = get_liveboard(station=station)
    if data and "departures" in data:
        departures = data["departures"].get("departure", [])
        insert_departures(departures)
        return func.HttpResponse(
            f"{len(departures)} départs insérés pour {station}.",
            status_code=200
        )
    else:
        return func.HttpResponse("Aucune donnée à insérer.", status_code=200)
