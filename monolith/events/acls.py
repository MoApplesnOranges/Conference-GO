from .api_keys import PEXELS_API_KEY, OPEN_WEATHER_API_KEY
import requests
import json

def get_photo(city, state):
    url = "https://api.pexels.com/v1/search"
    photo = {
        "query": f"{city}, {state}"
    }
    headers = {"Authorization": PEXELS_API_KEY}
    response = requests.get(url, params=photo, headers=headers)
    content = response.json()
    try:
        picture_url = content["photos"][0]["src"]["original"]
        return {"picture_url": picture_url}
    except (KeyError, IndexError):
        return {"picture_url": None}

# get_photo("Tampa", "Florida")

def get_weather_data(city, state):
    # get the latitude and longitude of city and state
    url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {"q": f"{city}, {state}", "appid": OPEN_WEATHER_API_KEY}
    response = requests.get(url, params=params)
    content = response.json()
    lat = content[0]["lat"]
    lon = content[0]["lon"]

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": lat, "lon": lon, "units": "imperial", "appid": OPEN_WEATHER_API_KEY}
    response = requests.get(url, params=params)
    content = response.json()
    description = content["weather"][0]["description"]
    temperature = content["main"]["temp"]
    return {"description": description, "temperature": temperature, "longitude": lon, "latitude": lat}

# get_weather_data("New York", "New York")
