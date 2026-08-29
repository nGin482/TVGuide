import logging
import sys

dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter(
    '[{asctime}] [{levelname}] {name}: {message}', dt_fmt, style='{'
)

logging_handler = logging.StreamHandler(sys.stdout)
logging_handler.setFormatter(formatter)


def logging_app(log_info: str, level = logging.DEBUG):
    logging.basicConfig(
        filename='tvguide.log',
        filemode='a',
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

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