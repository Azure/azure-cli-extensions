import sys
import re
from enum import Enum, auto

from knack.log import get_logger

from azext_ai_did_you_mean_this.util import cached

logger = get_logger(__name__)

MODULE_MATCH_REGEX = r'{module}\s+\(([\d.]+)\)'


def _get_latest_package_version_from_pypi(module):
    from subprocess import check_output, STDOUT, CalledProcessError

    try:
        cmd = [sys.executable] + \
            f'-m pip search {module} -vv --disable-pip-version-check --no-cache-dir --retries 0'.split()
        logger.debug('Running: %s', cmd)
        log_output = check_output(cmd, stderr=STDOUT, universal_newlines=True)
        pattern = MODULE_MATCH_REGEX.format(module=module)
        matches = re.search(pattern, log_output)
        return matches.group(1) if matches else None
    except CalledProcessError:
        pass

    return None


class CliStatus(Enum):
    OUTDATED = auto()
    UP_TO_DATE = auto()
    UNKNOWN = auto()


@cached(cache_if=(CliStatus.OUTDATED, CliStatus.UP_TO_DATE))
def is_cli_up_to_date():
    from distutils.version import LooseVersion
    from azure.cli.core import __version__
    installed_version = LooseVersion(__version__)
    latest_version = _get_latest_package_version_from_pypi('azure-cli-core')

    result = CliStatus.UNKNOWN

    if latest_version is None:
        return result

    latest_version = LooseVersion(latest_version)
    is_up_to_date = installed_version >= latest_version
    result = CliStatus.UP_TO_DATE if is_up_to_date else CliStatus.OUTDATED
    return result
