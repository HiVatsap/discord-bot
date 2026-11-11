import datetime
import json
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup
import requests

from logger import logger

url = "https://bezsvitla.com.ua/chernihivska-oblast/cherha-6-2"
headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)

connect = True
light_intervals_str = None
light_status = None

if response.status_code == 200:
    soup = BeautifulSoup(response.content, "html.parser")

    countdown_div = soup.find("div", {"class": "bz-schedule-countdown"})
    if countdown_div:

        intervals_raw = countdown_div.get("data-schedule-intervals")
        if intervals_raw:
            intervals_json = intervals_raw.replace("&quot;", '"')
            intervals = json.loads(intervals_json)

            now = datetime.datetime.now(ZoneInfo("Europe/Kyiv"))
            current_time = now.strftime("%H:%M")

            current_status = "Неизвестно"
            if intervals:
                light_intervals = []
                for item in intervals:
                    start = item.get("from")
                    end = item.get("to")
                    state = item.get("state")

                    if state == "OFF":
                        light_intervals.append(f"> `{start} - {end}`")

                    if start <= current_time < end:
                        if state == "ON":
                            light_status = True
                        if state == "OFF":
                            light_status = False

                light_intervals_str = ("\n".join(light_intervals) if light_intervals else None)
            else:
                logger.error("График пуст")
        else:
            connect = False
            logger.error("Выполнение команды отменено: Не удалось определить график")
    else:
        connect = False
        logger.error("Выполнение команды отменено: Произошла ошибка при попытке обработать данные сайта")
else:
    connect = False
    logger.error(
        f"Выполнение команды отменено: Не удалось установить соединение с сайтом. HTTP код: {response.status_code}"
    )