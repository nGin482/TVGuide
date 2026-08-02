from __future__ import annotations
from datetime import datetime
import logging
import re

from data_validation.validation import Validation


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