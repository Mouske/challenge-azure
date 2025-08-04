import requests

def get_liveboard(station):
    url = f"https://api.irail.be/liveboard/?station={station}&format=json"
    response = requests.get(url)
    data = response.json()
    return data

# Test
data = get_liveboard("Brussels")
print(data)
