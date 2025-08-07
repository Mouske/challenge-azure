import requests
import json
from datetime import datetime

# url = "https://api.irail.be/liveboard/?station=Gent-Sint-Pieters&arrdep=departure&format=json&lang=fr"
# response = requests.get(url)

# if response.status_code == 200:
#     data = response.json()
#     print(data)
# else:
#     print("Erreur :", response.status_code)

def get_train_departures_json(station="Gent-Sint-Pieters"):
    """
    Récupère les départs de trains et retourne un JSON normalisé
    
    Args:
        station (str): Nom de la gare
    
    Returns:
        dict: Données formatées en JSON ou None en cas d'erreur
    """
    url = f"https://api.irail.be/liveboard/?station={station}&arrdep=departure&format=json&lang=fr"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Vérification de la présence des données
        if not data or 'departures' not in data:
            return {"error": "Aucune donnée de départ disponible"}
        
        # Normalisation des départs
        formatted_departures = []
        for dep in data['departures']['departure']:
            formatted_dep = {
                "heure": datetime.fromtimestamp(int(dep['time'])).strftime('%H:%M'),
                "destination": dep['station'],
                "voie": dep.get('platform', None),
                "train": dep.get('vehicle', None),
                "retard_minutes": int(dep.get('delay', 0)) // 60,
                "timestamp": int(dep['time']),
                "heure_prevue": datetime.fromtimestamp(int(dep['time']) - int(dep.get('delay', 0))).strftime('%H:%M')
            }
            formatted_departures.append(formatted_dep)
        
        # Construction du JSON normalisé
        result = {
            "gare": data.get('stationinfo', {}).get('name', 'Inconnue'),
            "heure_mise_a_jour": datetime.now().isoformat(),
            "nombre_departs": len(formatted_departures),
            "departs": formatted_departures,
            "statut": "success"
        }
        
        return result
        
    except requests.exceptions.RequestException as e:
        return {"error": f"Erreur de connexion: {str(e)}", "statut": "error"}
    except json.JSONDecodeError as e:
        return {"error": f"Erreur de décodage JSON: {str(e)}", "statut": "error"}
    except Exception as e:
        return {"error": f"Erreur inattendue: {str(e)}", "statut": "error"}

# Exécution du code
if __name__ == "__main__":
    result = get_train_departures_json()
    print(json.dumps(result, indent=2, ensure_ascii=False))

