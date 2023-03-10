import os
import random
import string
from knack.log import get_logger
from .dashboardApi import search_snapshot, get_snapshot
from .commons import print_horizontal_line, save_json

logger = get_logger(__name__)


def save_snapshots(grafana_url, backup_dir, timestamp, http_headers, **kwargs):
    folder_path = '{0}/snapshots/{1}'.format(backup_dir, timestamp)
    'snapshots_{0}.txt'.format(timestamp)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    get_all_snapshots_and_save(folder_path, grafana_url, http_get_headers=http_headers)
    print_horizontal_line()


def save_snapshot(file_name, snapshot_setting, folder_path):
    file_name = file_name.replace('/', '_')
    random_suffix = "".join(random.choice(string.ascii_letters) for _ in range(6))
    file_path = save_json(file_name + "_" + random_suffix, snapshot_setting, folder_path, 'snapshot')
    logger.warning("Snapshot: \"%s\" is saved", snapshot_setting.get('dashboard', {}).get("title"))
    logger.info("    -> %s", file_path)


def get_single_snapshot_and_save(snapshot, grafana_url, http_get_headers, folder_path):
    (status, content) = get_snapshot(snapshot['key'], grafana_url, http_get_headers)
    if status == 200:
        save_snapshot(snapshot['name'], content, folder_path)
    else:
        logger.warning("Getting snapshot %s FAILED, status: %s, msg: %s", snapshot['name'], status, content)


def get_all_snapshots_and_save(folder_path, grafana_url, http_get_headers):
    status_code_and_content = search_snapshot(grafana_url, http_get_headers)
    if status_code_and_content[0] == 200:
        snapshots = status_code_and_content[1]
        logger.info("There are %s snapshots:", len(snapshots))
        for snapshot in snapshots:
            logger.info(snapshot)
            get_single_snapshot_and_save(snapshot, grafana_url, http_get_headers, folder_path)
    else:
        logger.warning("Query snapshot failed, status: %s, msg: %s", status_code_and_content[0],
                       status_code_and_content[1])
