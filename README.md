# Is It a Good Time for a Walk?

***This is my final project submission for CS50p: Introduction to Python***.

## Video

[Video Link](https://www.youtube.com/watch?v=hd92i05l9xo)

## Introduction

As someone from a warmer and (way) sunnier country, I realized after moving to the UK how much more time I want to spend outdoors when the weather is nice. Moving to a city that is extremely walkable, I found myself wanting to get out of the house for a walk particularly when the sky is blue and sun is shining - even when it is cold - and, conversely, not wanting to leave the house even when there is light rain. This observation led me to conversations about how people can have different preferences for weather.

So for my final project for CS50p, I decided to create a command-line application that helps users determine if the current weather conditions are suitable for taking a walk based on their preferences. The program collects real-time weather data and calculates a customised score by considering several weather factors weighted by importance specified by the user.

## How It Works

The application uses [OpenWeatherMap API](https://openweathermap.org/api) to retrieve real-time weather data for any city worldwide. The user has to enter a city name in the command line (denoted by "-l" or "--location"). It then processes the data for the selected city through a scoring algorithm. The weather attributes taken into account are:
1. Temperature (in degrees Celsius)
2. Rain fall (in mm/hour)
3. Wind speed (in m/s)
4. Cloud cover (in %)
5. Time of day (daytime or nighttime)

Users can customize how much each factor affects the final score in the command-line, however, these are optional. The time of day attribute asks for a binary input ("yes" means the user prefers going for a walk **only** during the day, "no" means no preference for daytime). This personalization allows the weather score to reflect individual preferences/tolerances.

### Features

- Real-time weather data retrieval
- Customisable importance weights for weather attributes
- Daytime-only option for users who do not prefer to walk at nighttime.
- Scoring system that calculates a final score between 0 to 100 and provides recommendations.
- Error handling

## Implementation

The project consists of a new class called WeatherData and several helper functions.

The **WeatherData** class processes the JSON data collected from the API response. Then, it parses and stores the data in an instantiated object. The class also has methods to determine if it is currently daytime or nighttime, and compute the personalized weather score.

The helper functions do the following:
- **get_weather_data()**: Handles communication with the API and retrieves the JSON data.
- **parse_prefs()**: Processes command-line arguments using [argparse](https://docs.python.org/3/library/argparse.html).
- **normalize_preferences()**: Validates the preferences and normalizes the values to be passed on to the score function.

The project has the dependencies [argparse](https://docs.python.org/3/library/argparse.html), [datetime](https://docs.python.org/3/library/datetime.html), [pytest](https://pypi.org/project/pytest/), [requests](https://pypi.org/project/requests/), [unittest.mock](https://docs.python.org/3/library/unittest.mock.html).

## Usage

To use the application, run the script as follows:

```
python project.py -l "City name" [-t 1-5] [-r 1-5] [-w 1-5] [-c 1-5] [-d yes/no]
```

**Arguments**
  - "-l"/"--location": **(Required)** City name
  - "-t"/"--temperature": Temperature importance (1-5)
  - "-r"/"--rain": Rain importance (1-5)
  - "-w"/"--wind": Wind importance (1-5)
  - "-c"/"--clouds": Cloud cover importance (1-5)
  - "-d"/"--d": Daytime ("yes" or "no")

***e.g.***

```
# without optional arguments
python project.py -l London

# with optional arguments
python project.py -l London -t 4 -r 5 -w 2 -c 3 -d yes
```

## Design Choices

The factors and their respective weightings are below:
1. Temperature, with weight 40.
2. Rain, with weight 30.
3. Wind, with weight 20.
4. Cloud cover, with weight 10.
5. Time of day, no weighting.

_These weights add up to 100 and can be adjusted by the programmer._

The first 4 attributes can be given a score from 1 to 5 (1 being not important, and 5 being very important) and have default values of 3. The time of day attribute has the default value "no".

The starting score is 100. Deductions are made based on deviations from "ideal" conditions and there are caps for deviations, beyond which maximum points are deducted for that respective attribute. This approach was selected to keep the scoring system intuitive and make the final scores easy to compare.

The considerations for ideal conditions as well as the caps for each weather attribute can be found below:
  - Temperature
    - Ideal temperature range: 15-25 degrees Celsius _(no deduction)_
    - Temperature deviation cap: 10 degrees Celsius _(i.e., temperatures below 5 degrees and above 35 degrees cause maximum deduction)_
  - Rain
    - Ideal rain: 0 millimetres per hour (mm/hr)
    - Cap for rain: 5 mm/hr _(middle value of "moderate rain" classification)_
  - Wind
    - Ideal wind: 0-3 meters per second (m/s) _(upper limit of "light breeze" classification)_
    - Cap for wind: 11 m/s _(upper limit of "moderate breeze" classification: "Large branches sway, umbrellas difficult to use")_
  - Cloud cover
    - Ideal: 0%

The preferences are normalised such that the normalised versions of the default values for the attributes are equal to 1. This means that we can have the full range of scores (0-100) in the default values.

## Challenges

I tried to add as many concepts as possible from the course, in particular the last two weeks, without adding parts which would have been irrelevant to the main purpose of the application. This caused the code to be a fair bit longer than I anticipated, and, at times, make it difficult to follow of the code. As every output had a different output class, I added type hints, which was very helpful. Another aspect which I wanted to touch on with my final project was using an API extensively. This proved to be a somewhat steep learning curve, especially with regards to handling errors and testing. I had to learn about the unittest.mock package to mock API calls and test the get_weather_data() function.

The mathematical reasoning for the scoring system might not be the most robust, but I wanted to make it as intuitive as possible since the main focus of this project is the execution of the code, not the mathematical accuracy.

## Future Improvements

More optional weather attributes can be added, as the data retrieved has many more attributes(e.g., humidity, felt temperature). Support for providing a second (or multiple) location(s) can be added to allow for direct comparisons. Historical data can be analysed to give predictions for the best times to go for a walk for the next 24 hours (or next week etc.). For the movie recommendation for subpar conditions, I considered adding a randomly selected movie from a .csv file containing IMDB's top 250 rated movies to make use of the learnings from Week 6: File I/O.

## Thank You

FINALLY: **Thank you to the amazing CS50 team** for the highly engaging course from start to finish! I had attempted to learn programming languages a few times prior to this, but this course helped me to stick with it. I will continue my learning with the other CS50 courses.
