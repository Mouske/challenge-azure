from irail_api import get_liveboard
from database import insert_departures

def main():
    data = get_liveboard()
    if data and "departures" in data:
        departures = data["departures"].get("departure", [])
        insert_departures(departures)
        print(f"{len(departures)} départs insérés dans la base de données.")
    else:
        print("Aucune donnée à insérer.")

if __name__ == "__main__":
    main()
