import logging

logger = logging.getLogger('aiotime')


def logging_handler(data):
    logger.info(str(data))
