from knack.log import get_logger

from .backup import backup
from .restore import restore

logger = get_logger(__name__)


def migrate(backup_grafana_name, backup_url, backup_directory, components, backup_headers,
            restore_url, restore_headers, data_sources, folders_to_include=None, folders_to_exclude=None):

    archive_file = backup(grafana_name=backup_grafana_name,
                          grafana_url=backup_url,
                          backup_dir=backup_directory,
                          components=components,
                          http_headers=backup_headers,
                          folders_to_include=folders_to_include,
                          folders_to_exclude=folders_to_exclude)

    restore(grafana_url=restore_url,
            archive_file=archive_file,
            components=components,
            http_headers=restore_headers,
            destination_datasources=data_sources)