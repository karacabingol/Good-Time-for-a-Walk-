from argparse import Namespace
import pytest
import requests
from unittest.mock import patch, Mock
from project import WeatherData, get_weather_data, normalize_preferences

# example retrieved from https://openweathermap.org/current#example_JSON
# The relevant values have been altered to start with perfect conditions and make calculations more straightforward.
example_weather_data = {
    "coord": {"lon": 7.367, "lat": 45.133},
    "weather": [{"id": 501, "main": "Rain", "description": "moderate rain", "icon": "10d"}],
    "base": "stations",
    "main": {"temp": 20, "feels_like": 282.93, "temp_min": 283.06, "temp_max": 286.82, "pressure": 1021, "humidity": 60, "sea_level": 1021, "grnd_level": 910},
    "visibility": 10000,
    "wind": {"speed": 3, "deg": 121, "gust": 3.47},
    # "rain": {"1h": 2.73},
    "clouds": {"all": 0},
    "dt": 1726660758,
    "sys": {"type": 1, "id": 6736, "country": "IT", "sunrise": 1726636384,"sunset": 1726680975},
    "timezone": 7200,
    "id": 3165523,
    "name": "Province of Turin",
    "cod": 200
    }

default_normalized_preferences = {"temperature": 1, "rain": 1, "wind": 1, "clouds": 1, "daytime": "no"}


def test_score():
    weather_data = WeatherData(example_weather_data)
    assert weather_data.score(default_normalized_preferences) == 100

    weather_data.temperature = 5
    assert weather_data.score(default_normalized_preferences) == 60

    weather_data.rain = 10
    assert weather_data.score(default_normalized_preferences) == 30

    weather_data.wind = 11
    assert weather_data.score(default_normalized_preferences) == 10

    weather_data.clouds = 100
    assert weather_data.score(default_normalized_preferences) == 0


@patch("project.requests.get")
def test_get_weather_data(mock_get):
    # create a mock object
    mock_response = Mock()

    global example_weather_data
    # define the JSON data this object should return
    mock_response.json.return_value = example_weather_data

    # mock requests.get method to return mock response
    mock_get.return_value = mock_response

    result = get_weather_data("Oxford")
    assert isinstance(result, WeatherData)

@patch("project.requests.get")
def test_get_weather_data_fail(mock_get):
    mock_get.side_effect = requests.RequestException()
    with pytest.raises(ValueError):
        get_weather_data("Oxford")


def test_normalize_preferences():
    test_args = Namespace(temperature = 4, rain = 3, clouds = 2, wind = 1, daytime = "no")
    assert normalize_preferences(test_args) == {"temperature": 4/3, "rain": 1, "clouds": 2/3, "wind": 1/3, "daytime": False}

def test_normalize_preferences_invalid():
    with pytest.raises(ValueError):
        normalize_preferences(Namespace(temperature = 6, rain = 3, clouds = 3, wind = 3, daytime = "no"))
    with pytest.raises(ValueError):
        normalize_preferences(Namespace(temperature = 3, rain = 0, clouds = 3, wind = 3, daytime = "no"))
    with pytest.raises(ValueError):
        normalize_preferences(Namespace(temperature = 3, rain = 3, clouds = 3, wind = 3, daytime = "maybe"))

