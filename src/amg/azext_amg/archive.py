from glob import glob
import os
import tarfile
import shutil
from knack.log import get_logger

logger = get_logger(__name__)


def archive(backup_dir, timestamp):
    archive_file = '{0}/{1}.tar.gz'.format(backup_dir, timestamp)
    backup_files = []

    for folder_name in ['folders', 'datasources', 'dashboards', 'alert_channels', 'organizations', 'users', 'snapshots', 'versions', 'annotations']:
        backup_path = '{0}/{1}/{2}'.format(backup_dir, folder_name, timestamp)

        for file_path in glob(backup_path):
            logger.info('backup %s at: %s', folder_name, file_path)
            backup_files.append(file_path)

    if os.path.exists(archive_file):
        os.remove(archive_file)

    with tarfile.open(archive_file, "w:gz") as tar:
        for file_path in backup_files:
            tar.add(file_path)
            if not os.environ.get("AMG_DEBUG", False):
                shutil.rmtree(os.path.abspath(os.path.join(file_path, os.pardir)))
    tar.close()
    logger.warning('Created archive at: %s', archive_file)
