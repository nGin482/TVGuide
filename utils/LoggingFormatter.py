import logging
import sys

dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter(
    '[{asctime}] [{levelname}] {name}: {message}', dt_fmt, style='{'
)

logging_handler = logging.StreamHandler(sys.stdout)
logging_handler.setFormatter(formatter)
