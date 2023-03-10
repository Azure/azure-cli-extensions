import os
import time
from knack.log import get_logger
from .dashboardApi import search_annotations
from .commons import print_horizontal_line, save_json

logger = get_logger(__name__)


def save_annotations(grafana_url, backup_dir, timestamp, http_headers, **kwargs):
    folder_path = '{0}/annotations/{1}'.format(backup_dir, timestamp)
    'annotations_{0}.txt'.format(timestamp)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    get_all_annotations_and_save(folder_path, grafana_url, http_get_headers=http_headers)
    print_horizontal_line()


def save_annotation(file_name, annotation_setting, folder_path):
    file_path = save_json(file_name, annotation_setting, folder_path, 'annotation')
    logger.warning("Annotation: \"%s\" is saved", annotation_setting.get('text'))
    logger.info("    -> %s", file_path)


def get_all_annotations_and_save(folder_path, grafana_url, http_get_headers):
    now = int(round(time.time() * 1000))
    one_month_in_ms = 31 * 24 * 60 * 60 * 1000

    ts_to = now
    ts_from = now - one_month_in_ms
    thirteen_months_retention = (now - (13 * one_month_in_ms))

    while ts_from > thirteen_months_retention:
        status_code_and_content = search_annotations(grafana_url, ts_from, ts_to, http_get_headers)
        if status_code_and_content[0] == 200:
            annotations_batch = status_code_and_content[1]
            logger.info("There are %s annotations:", len(annotations_batch))
            for annotation in annotations_batch:
                logger.info(annotation)
                save_annotation(str(annotation['id']), annotation, folder_path)
        else:
            logger.warning("Query annotation FAILED, status: %s, msg: %s", status_code_and_content[0],
                           status_code_and_content[1])

        ts_to = ts_from
        ts_from = ts_from - one_month_in_ms
