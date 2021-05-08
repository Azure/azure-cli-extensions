import logging
import sys

def setup_logging(root_logger_name="", log_path="az_aks_tool.log"):
    if root_logger_name == "":
        try:
            root_logger_name = __name__.split(".")[0]
        except Exception as e:
            print("Failed to parse module name from '{}', error: {}".format(__name__, e))
    logger = logging.getLogger(root_logger_name)
    logger.setLevel(level=logging.DEBUG)

    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # FileHandler
    file_handler = logging.FileHandler(filename=log_path, mode="w")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level=logging.DEBUG)
    logger.addHandler(file_handler)

    # StreamHandler
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(level=logging.INFO)
    logger.addHandler(stream_handler)
