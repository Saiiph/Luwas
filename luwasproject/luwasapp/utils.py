import requests

def get_geolocation_data():
    api_key = "01e65699cfb6490490e283bd64dc465c"
    base_url = "https://ipgeolocation.abstractapi.com/v1/"
    params = {
        "api_key": api_key,
    }
    
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    return None
