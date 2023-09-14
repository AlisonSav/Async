import asyncio
import datetime
import json
import time
from statistics import mean

import aiohttp

from dotenv import load_dotenv

load_dotenv()

today = datetime.date.today()
print("Today is:", today)  # noqa: T201
year = today.strftime("%Y")
month = today.strftime("%m")
day = today.strftime("%d")


async def get_weather_7timer(session):
    url = "https://www.7timer.info/bin/civillight.php?lon=50&lat=30.5&ac=0&unit=metric&output=json&tzshift=0"

    async with session.get(url=url) as response:
        data = await response.read()
        weather = json.loads(data)
        for date_dict in weather["dataseries"]:
            if date_dict["date"] == int(f"{year}{month}{day}"):
                max_temperature = date_dict["temp2m"]["max"]
                min_temperature = date_dict["temp2m"]["min"]
                temp = (max_temperature + min_temperature) / 2
        return temp


async def get_weather_open_meteo(session):
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude=50.45&longitude=30.5&daily=temperature_2m_max&"
        f"start_date={year}-{month}-{day}&end_date={year}-{month}-{day}&timezone=auto"
    )

    async with session.get(url=url) as response:
        data = await response.read()
        weather = json.loads(data)
        weather = weather["daily"]["temperature_2m_max"][0]
        return weather


async def get_weather_weatherstack(session):
    url = "https://api.oceandrivers.com/v1.0/getWeatherDisplay/kyiv/?period=latestdata"
    async with session.get(url=url) as response:
        data = await response.read()
        weather = json.loads(data)
        weather = weather["TEMPERATURE"]
        return weather


async def results():
    async with aiohttp.ClientSession() as session:
        res = await asyncio.gather(
            get_weather_7timer(session),
            get_weather_open_meteo(session),
            get_weather_weatherstack(session),
        )
        print("results:", res)  # noqa: T201
        print(f"The average temperature today will be: {round(mean(res))}")  # noqa: T201


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(results())
    duration = time.time() - start_time
    print(f"Operation's time: {duration} seconds")  # noqa: T201
