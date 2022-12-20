from glob import glob
import tarfile
import tempfile
import collections

from azure.cli.core.azclierror import ArgumentUsageError
from knack.log import get_logger

from .create_folder import create_folder
from .create_dashboard import create_dashboard
from .create_snapshot import create_snapshot
from .create_annotation import create_annotation
from .create_datasource import create_datasource

logger = get_logger(__name__)


def restore(grafana_url, archive_file, components, http_headers):
    try:
        tarfile.is_tarfile(name=archive_file)
    except IOError as e:
        raise ArgumentUsageError(f"failed to open {archive_file} as a tar file") from e

    # Shell game magic warning: restore_function keys require the 's'
    # to be removed in order to match file extension names...
    restore_functions = collections.OrderedDict()
    restore_functions['folder'] = create_folder
    restore_functions['dashboard'] = create_dashboard
    restore_functions['snapshot'] = create_snapshot
    restore_functions['annotation'] = create_annotation
    restore_functions['datasource'] = create_datasource

    with tarfile.open(name=archive_file, mode='r:gz') as tar:
        with tempfile.TemporaryDirectory() as tmpdir:
            tar.extractall(tmpdir)
            tar.close()
            restore_components(grafana_url, restore_functions, tmpdir, components, http_headers)


def restore_components(grafana_url, restore_functions, tmpdir, components, http_headers):

    if components:
        exts = [c[:-1] for c in components]
    else:
        exts = list(restore_functions.keys())
    if "folder" in exts:  # make "folder" be the first to restore, so dashboards can be positioned under a right folder
        exts.insert(0, exts.pop(exts.index("folder")))

    for ext in exts:
        for file_path in glob('{0}/**/*.{1}'.format(tmpdir, ext), recursive=True):
            logger.warning('Restoring %s: %s', ext, file_path)
            restore_functions[ext](grafana_url, file_path, http_headers)
