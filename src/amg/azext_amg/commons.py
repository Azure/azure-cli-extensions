import re
import json

from knack.log import get_logger

logger = get_logger(__name__)


def print_horizontal_line():
    logger.info('')
    logger.info("########################################")
    logger.info('')


def log_response(resp):
    status_code = resp.status_code
    logger.debug("[DEBUG] resp status: %s", status_code)
    try:
        logger.debug("[DEBUG] resp body: %s", resp.json())
    except ValueError:
        logger.debug("[DEBUG] resp body: %s", resp.text)
    return resp


def save_json(file_name, data, folder_path, extension, pretty_print=None):
    pattern = "^db/|^uid/"
    if re.match(pattern, file_name):
        file_name = re.sub(pattern, '', file_name)

    file_path = folder_path + '/' + file_name + '.' + extension
    with open("{0}".format(file_path), 'w', encoding="utf8") as f:
        if pretty_print:
            f.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
        else:
            f.write(json.dumps(data))
    # Return file_path for showing in the console message
    return file_path
