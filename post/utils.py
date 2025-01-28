import logging
import time
import requests

# Logging setup
def setup_logger(silent=False):
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if not silent else logging.CRITICAL)
    return logger

# Retry function for API calls
def retry_request(func, retries=3, delay=2, *args, **kwargs):
    attempt = 0
    while attempt < retries:
        try:
            return func(*args, **kwargs)
        except requests.exceptions.RequestException as e:
            attempt += 1
            if attempt < retries:
                time.sleep(delay)
            else:
                raise e
