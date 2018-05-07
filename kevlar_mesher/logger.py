import logging


def get_logger() -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s'
    )

    logger = logging.getLogger('mesher')
    logger.setLevel(logging.INFO)

    return logger
