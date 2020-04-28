import sys
import re
import threading
from enum import Enum, auto

from knack.log import get_logger
from azure.cli.core.util import check_connectivity

from azext_ai_did_you_mean_this.util import cached

logger = get_logger(__name__)

MODULE_MATCH_REGEX = r'{module}\s+\(([\d.]+)\)'

_async_is_up_to_date = threading.Event()
_async_has_checked_for_updates = threading.Event()
_async_unknown_update_status = threading.Event()


def _get_latest_package_version_from_pypi(module):
    from subprocess import check_output, STDOUT, CalledProcessError

    if not check_connectivity(max_retries=0):
        return None

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


def reset_cli_update_status():
    EVENTS = (
        _async_has_checked_for_updates,
        _async_is_up_to_date,
        _async_unknown_update_status
    )

    for event in EVENTS:
        if event.is_set():
            event.clear()


@cached(cache_if=(CliStatus.OUTDATED, CliStatus.UP_TO_DATE))
def is_cli_up_to_date():
    from distutils.version import LooseVersion
    from azure.cli.core import __version__
    installed_version = LooseVersion(__version__)
    latest_version = _get_latest_package_version_from_pypi('azure-cli-core')

    result = CliStatus.UNKNOWN

    if latest_version is None:
        _async_unknown_update_status.set()
        _async_has_checked_for_updates.set()
        return result

    latest_version = LooseVersion(latest_version)
    is_up_to_date = installed_version >= latest_version
    if is_up_to_date:
        _async_is_up_to_date.set()
    else:
        _async_is_up_to_date.clear()
    _async_has_checked_for_updates.set()
    result = CliStatus.UP_TO_DATE if is_up_to_date else CliStatus.OUTDATED
    return result


@cached(cache_if=(CliStatus.OUTDATED, CliStatus.UP_TO_DATE))
def async_is_cli_up_to_date(wait=False, timeout=None):
    if _async_has_checked_for_updates.is_set():
        logger.debug('Already checked for updates.')
    # if we should wait on checking if the cli is up to date...
    if wait or timeout is not None:
        # wait for at most timeout seconds.
        _async_has_checked_for_updates.wait(timeout)
    timed_out = not _async_has_checked_for_updates.is_set()
    # otherwise, if the status is unknown or if the check for updates is incomplete
    if _async_unknown_update_status.is_set() or timed_out:
        if timed_out:
            logger.debug('Check for CLI update status timed out.')
        # indicate that the status of the CLI is unknown
        return CliStatus.UNKNOWN
    # if we've chekced for updates already, return the status retrieved by that check.
    return CliStatus.UP_TO_DATE if _async_is_up_to_date.is_set() else CliStatus.OUTDATED
