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

    return logger
