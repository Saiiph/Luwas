import requests

def get_location_from_coordinates(lat, lng):
    api_key = '0addd8efb8194cebb0d715a1cb3d980d'
    url = f'https://api.opencagedata.com/geocode/v1/json?q={lat}+{lng}&key={api_key}'
    response = requests.get(url)
    data = response.json()
    
    if data['status']['code'] == 200:
        address = data['results'][0]['formatted']
        return address
    else:
        return "Location Not Found!"