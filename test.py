import requests

url = "https://api.irail.be/liveboard/?station=Gent-Sint-Pieters&arrdep=departure&format=json&lang=fr"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print("Erreur :", response.status_code)

