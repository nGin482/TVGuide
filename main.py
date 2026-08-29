from dotenv import load_dotenv
from requests import get
import logging
import os

os.environ['PYTHON_ENV'] = 'production'
from utils.logging_formatter import logging_handler

load_dotenv('.env')

logger = logging.getLogger("main")
logger.addHandler(logging_handler)
logger.setLevel(logging.DEBUG)

# https://epg.abctv.net.au/processed/events_Sydney_vera.json
# https://www.abc.net.au/tv/programs/vera/series-episode-index.json?_=1555488755177


def find_json(url: str):
    data = get(url).json()

    return data


def search_vera_series():

    url = 'https://www.abc.net.au/tv/programs/vera/series-episode-index.json?_=1555488755177'

    try:
        data = find_json(url)
        series_num = int(data[-1]['seriesNumber'])
    except ValueError:
        # print(e.msg)
        code = get(url).status_code
        series_num = "ABC's Vera page is responding with " + str(code) + " and is temporarily unavailable"

    return series_num


if __name__ == '__main__':
    from services.hermes.hermes import hermes

    try:
        hermes.run(os.getenv('HERMES'))
    except KeyboardInterrupt:
        logger.info("Hermes exiting")

    # {"id": "content_wrapper_inner"}
