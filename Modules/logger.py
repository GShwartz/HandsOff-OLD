import logging
import logging.handlers
import queue


def init_logger(log_path, name):
    log_queue = queue.Queue()
    queue_handler = logging.handlers.QueueHandler(log_queue)

    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        info = logging.FileHandler(log_path)
        info.setLevel(logging.DEBUG)
        info.setFormatter(formatter)
        logger.addHandler(info)

        # error = logging.FileHandler(log_path)
        # error.setLevel(logging.ERROR)
        # error.setFormatter(formatter)
        # logger.addHandler(error)
        #
        # warning = logging.FileHandler(log_path)
        # warning.setLevel(logging.WARNING)
        # warning.setFormatter(formatter)
        # logger.addHandler(warning)
        #
        # crit = logging.FileHandler(log_path)
        # crit.setLevel(logging.CRITICAL)
        # crit.setFormatter(formatter)
        # logger.addHandler(crit)

    return logger
