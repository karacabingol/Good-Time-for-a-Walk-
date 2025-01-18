from datetime import datetime
import argparse
import json
import requests
import sys

default_value = 3

class WeatherData:
    def __init__(self, weather_json):
        try:
            self.city = weather_json["name"]
            self.country = weather_json["sys"]["country"]
            self.temperature = weather_json["main"]["temp"]
            self.clouds = weather_json["clouds"]["all"]
            self.wind = weather_json["wind"]["speed"]

            # rain (and rain in the next hour) are optional - not present when there is no rain
            self.rain = weather_json.get("rain", {}).get("1h", 0)

            self.sunrise = datetime.fromtimestamp(weather_json["sys"]["sunrise"])
            self.current_time = datetime.fromtimestamp(weather_json["dt"])
            self.sunset = datetime.fromtimestamp(weather_json["sys"]["sunset"])

        except KeyError:
            raise ValueError("KeyError: Invalid city name")
        except (TypeError, ValueError) as e:
            raise ValueError(f"{e}: Data format invalid")


    def is_daytime(self) -> bool:
        return self.sunrise <= self.current_time <= self.sunset


    def score(self, user_preferences: dict) -> float:
        score = 100
        # weights of each variable - add up to 100.
        weights = {"temperature": 40, "rain": 30, "wind": 20, "clouds": 10}

        temp_ideal_min = 15
        temp_ideal_max = 25
        temp_cap = 10           # effect of deviation from ideal range is capped at 10.
        rain_cap = 5            # 5mm/hr rain is seen as moderate.
        wind_ideal_max = 3      # upper limit of the classification 'light breeze'.
        wind_cap = 11           # umbrellas difficult to be used beyond wind speeds of 11 m/s.

        # if temperature is within the ideal range, no impact. If outside, the impact caps when outside the range by 10 degrees Celsius.
        if self.temperature < temp_ideal_min or temp_ideal_max < self.temperature:
            if self.temperature < temp_ideal_min:
                temp_deviation = abs(self.temperature - temp_ideal_min)
            else:
                temp_deviation = abs(temp_ideal_max - self.temperature)
            temp_impact = min(temp_deviation / temp_cap, 1) * weights["temperature"]
        else:
            temp_impact = 0

        # anything above 5mm/hr caps the rain_impact variable.
        rain_impact = min(self.rain / rain_cap, 1) * weights["rain"]

        # percentage of cloud cover multiplied by the weighting.
        clouds_impact = self.clouds / 100 * weights["clouds"]

        if wind_ideal_max < self.wind:
            wind_deviation = self.wind - wind_ideal_max
            wind_impact = min(wind_deviation / (wind_cap - wind_ideal_max), 1) * weights["wind"]
        else:
            wind_impact = 0

        score -= (
            temp_impact * user_preferences["temperature"] +
            rain_impact * user_preferences["rain"] +
            clouds_impact * user_preferences["clouds"] +
            wind_impact * user_preferences["wind"]
        )

        return max(0, round(score, 1))


def get_weather_data(city) -> WeatherData:
    if len(sys.argv) < 2 or (len(sys.argv) == 2 and(sys.argv[1] == "-h" or sys.argv[1] == "--help")):
        raise ValueError("Please enter '-l' or '--location' followed by a city name. Type 'python.py -h' for more details.")

    api_key = "cf99b20cba48a363438ead4e08badd18"
    city = city.strip().capitalize()
    url = "https://api.openweathermap.org/data/2.5/weather"

    try:
        response = requests.get(url, params = {"q": city, "appid": api_key, "units": "metric"}, timeout = 5)
        return WeatherData(response.json())

    except requests.RequestException as e:
        raise ValueError(f"{e}: Error obtaining weather data")


def parse_prefs() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description = "Is the weather good enough for your preferences to go for a walk? 🚶")
    parser.add_argument("-l", "--location", required = True, type = str, help = "Your location")

    explain_scale = f"\033[37mPlease answer between 1-5 (1 being not important and 5 being very important).\033[0m"
    explain_default = f"\033[37m[Optional: default value is {default_value}].\033[0m"

    parser.add_argument(
        "-t", "--temperature", default = default_value, type = int,
        help = f"Temperature preference: How important is the temperature 🌡️ for you? {explain_scale} {explain_default}"
        )
    parser.add_argument(
        "-r", "--rain", default = default_value, type = int,
        help = f"Rain preference: How important is it for you that it is NOT raining 🌧️ ? {explain_scale} {explain_default}"
        )
    parser.add_argument(
        "-c", "--clouds", default = default_value, type = int,
        help = f"Cloud preference: How important is the level of cloud cover ⛅️ for you? {explain_scale} {explain_default}"
        )
    parser.add_argument(
        "-w", "--wind", default = default_value, type = int,
        help = f"Wind preference: How important is the level of wind 💨 for you? {explain_scale} {explain_default}"
        )
    parser.add_argument(
        "-d", "--daytime", default = "no", type = str,
        help = f"Do you only go out for a walk in daytime ☀️ ? \033[37mPlease answer 'yes' or 'no'.\033[0m"
        )

    return parser.parse_args()


def normalize_preferences(args) -> dict:
    if not all(1 <= pref <= 5 for pref in [args.temperature, args.rain, args.clouds, args.wind]):
        raise ValueError("Preferences for temperature 🌡️ , rain 🌧️ , cloud cover ⛅️, and wind 💨 must be between 1-5.")

    daytime_pref = args.daytime.strip().lower()
    if not daytime_pref in ["yes", "no"]:
        raise ValueError("Daytime preference ☀️ must be 'yes' or 'no'.")

    # dividing by the default_value instead of the max value.
    return {
        "temperature": args.temperature / default_value,
        "rain": args.rain / default_value,
        "clouds": args.clouds / default_value,
        "wind": args.wind / default_value,
        "daytime": args.daytime == "yes"
        }


def main():
    # weather_data = get_weather_data(input("Location: "))

    args = parse_prefs()

    try:
        preferences = normalize_preferences(args)
        weather_data = get_weather_data(args.location)
        weather_score = weather_data.score(preferences)

        if preferences["daytime"] and not weather_data.is_daytime():
            sys.exit("It's currently night time, and you indicated that you only prefer walking during the day.")

        print(
            "",
            f"Weather in {weather_data.city}, {weather_data.country} right now:",
            f"🌡️  Temperature is \033[34m{weather_data.temperature}\033[0m degrees Celsius.",
            sep = "\n"
            )
        if weather_data.rain > 0:
            print(f"🌧️ Rain forecasted for the next hour is \033[34m{weather_data.rain}\033[0m mm.")
        else:
            print("🌧️  \033[34mNo\033[0m rain is forecasted for the next hour.")

        print(
            f"💨 Wind speed is \033[34m{weather_data.wind}\033[0m m/s.",
            f"⛅️ Cloud cover is \033[34m{weather_data.clouds}%\033[0m.",
            sep = "\n"
            )
        print(f"\nBased on your preferences, the weather score is: \033[34m{weather_score}\033[0m out of 100.")

        if weather_score >= 85:
            print("These are excellent conditions! What are you waiting for?")
        elif weather_score >= 70:
            print("These are good conditions for a walk!")
        elif weather_score >= 50:
            print("These are average conditions for a walk.")
        elif weather_score >= 25:
            print("The conditions are below average, later might be a better idea perhaps..?")
        else:
            print("The conditions are terrible! I'd recommend staying in and watching a movie. I heard Gladiator is a good one...")

    except ValueError as e:
        sys.exit(f"{e}\nPlease refer to the Read Me file, or type 'python project.py -h' in the terminal for more details.")


if __name__ == "__main__":
    main()
