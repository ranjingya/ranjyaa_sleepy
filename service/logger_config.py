import logging
import sys
import os


def create_custom_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s [%(levelname)-5s] %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    log_file = os.path.join(os.getcwd(), 'service.log')
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
