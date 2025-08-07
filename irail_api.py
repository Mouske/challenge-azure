# Server=tcp:trainproject2.database.windows.net,1433;Initial Catalog=TrainDB2;Persist Security Info=False;User ID=azureadmin;Password={your_password};MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;

import requests

def get_liveboard(station="Gent-Sint-Pieters", lang="fr"):
    url = f"https://api.irail.be/liveboard/?station={station}&arrdep=departure&format=json&lang={lang}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print("Erreur API iRail:", response.status_code)
        return None
