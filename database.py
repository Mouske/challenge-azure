import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

def connect_db():
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={os.getenv('DB_SERVER')},1433;"
        f"DATABASE={os.getenv('DB_NAME')};"
        f"UID={os.getenv('DB_USER')};"
        f"PWD={os.getenv('DB_PASSWORD')};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )
    return conn

def insert_departures(departures):
    conn = connect_db()
    cursor = conn.cursor()

    for dep in departures:
        station = dep.get("station")
        time_unix = dep.get("time")
        # Conversion en datetime si nécessaire
        # from datetime import datetime
        # departure_time = datetime.fromtimestamp(time_unix) if time_unix else None
        
        vehicle = dep.get("vehicle")
        platform = str(dep.get("platform", None))  # Toujours string pour SQL
        delay = dep.get("delay", 0)

        cursor.execute("""
            INSERT INTO Departures (station, [time], vehicle, platform, delay)
            VALUES (?, ?, ?, ?, ?)
        """, (station, time_unix, vehicle, platform, delay))

    conn.commit()
    cursor.close()
    conn.close()

