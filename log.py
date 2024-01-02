from __future__ import annotations
from datetime import datetime
import logging
import json
import os
import re

from data_validation.validation import Validation
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from database.models.GuideShow import GuideShow


def get_date_from_tvguide_message(message: str):
    """
    Get the date that TVGuide message was sent. Receives the message as a parameter.
    Returns `None` if the date could not be found in the message
    """
    message_header_search = re.search(r'\d{2}-\d{2}-\d{4} TVGuide', message)
    if message_header_search is not None:
        message_date_search = re.findall(r'\d+', message_header_search.group())
        datetime_values = [int(value) for value in message_date_search]
        date_of_latest_message = datetime(datetime_values[2], datetime_values[1], datetime_values[0])
        return date_of_latest_message
    else:
        return None


def compare_dates(date: datetime):

    if date.day != Validation.get_current_date().day:
        return True
    else:
        if date.hour <= 6:
            return True
        return False


def log_discord_message_too_long(message_length, fta_length):

    today_date = datetime.today().strftime("%d-%m-%Y")
    log_message = f'{today_date}\nDiscord tried sending the TVGuide message.\nThe maximum character length of a Discord message is 2000.\n \
        The length of this message is {message_length} and the length of the Free to Air portion is {fta_length}.\n \
            As a result, the message was split into the Free to Air and BBC portions and on the AM/PM portions of Free to Air.' 

    try:
        with open('log/message_logging.txt') as fd:
            current_log_contents = fd.read()
    except FileNotFoundError:
        current_log_contents = ''
            
    with open('log/message_logging.txt', 'w', encoding='utf-8') as fd:
        fd.write(f'{current_log_contents}\n\n\n{log_message}')

def logging_app(log_info: str, level = logging.DEBUG):
    logging.basicConfig(filename='tvguide.log', filemode='a', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    if level == logging.DEBUG:
        logging.debug(f"{log_info}")
    elif level == logging.INFO:
        logging.info(f"{log_info}")
    elif level == logging.WARNING:
        logging.warning(f"{log_info}")
    elif level == logging.ERROR:
        logging.error(f"{log_info}")
    elif level == logging.CRITICAL:
        logging.critical(f"{log_info}")