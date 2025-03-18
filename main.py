import atexit
import json
import logging.config
import logging.handlers

logger = logging.getLogger("logger")

def setup_logging():
    config_file = "logging_config.json"
    with open(config_file, "r") as file:
        config = json.load(file)

    logging.config.dictConfig(config)
    queue_handler = logging.getHandlerByName("queue_handler")
    if queue_handler is not None:
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)
        
def main():
    setup_logging()
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

    try:
        x = 1 / 0
    except ZeroDivisionError:
        logger.exception("You can't divide by zero")

    return

if __name__ == "__main__":
    main()