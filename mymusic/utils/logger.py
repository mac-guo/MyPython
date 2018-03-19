import mymusic.constants as constants
import logging


def getlogger():
    filehandler = logging.FileHandler(filename=constants.log_file_name, encoding="utf-8")
    formatter = logging.Formatter(fmt=constants.log_fmt, datefmt=constants.log_date_fmt)
    filehandler.setFormatter(formatter)
    logger = logging.getLogger(__name__)
    logger.addHandler(filehandler)
    logger.setLevel(logging.ERROR)
    return logger
