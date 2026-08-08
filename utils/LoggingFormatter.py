

import logging
import json
import sys

class LoggingFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname, 
            "severity_text": record.levelname,
            "message": record.getMessage(),
            "logger_name": record.name,
        }
        # Include exception info if it exists
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)


logging_handler = logging.StreamHandler(sys.stdout)
logging_handler.setFormatter(LoggingFormatter())
