# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Custom functions for azext_fzf.
"""

import io
import os
import platform
import shutil
import stat
import subprocess
import tarfile
import zipfile

import requests

from azure.cli.core.api import get_config_dir
from knack.log import get_logger
from knack.util import CLIError
from tabulate import tabulate


LOGGER = get_logger(__name__)


def _fzf_get_system():
    """
    Returns platform.system().

    Exists to be mocked in testing; if we just mock platform.system() it breaks the rest of
    azure-cli.
    """
    return platform.system()


def _fzf_get_filename():
    """
    Stub function to return the right command for each platform
    """
    if _fzf_get_system() == 'Windows':
        return "fzf.exe"
    return "fzf"


def _fzf_get_install_dir(install_dir=None):
    """
    Return the installation directory and check if it's in the PATH. Default: get_config_dir().
    """
    if not install_dir:
        install_dir = get_config_dir()
    else:
        if _fzf_get_system() == 'Windows':
            # be verbose, as the install_location likely not in Windows's search PATHs
            env_paths = os.environ['PATH'].split(';')
            env_paths_iter = (x for x in env_paths if x.lower().rstrip('\\') == install_dir.lower())
            found = next(env_paths_iter, None)
            if not found:
                # pylint: disable=logging-format-interpolation,line-too-long
                LOGGER.warning('Please add "{0}" to your search PATH so the `fzf` can be found. 2 options: \n'
                               '    1. Run "set PATH=%PATH%;{0}" or "$env:path += \'{0}\'" for PowerShell. '
                               'This is good for the current command session.\n'
                               '    2. Update system PATH environment variable by following '
                               '"Control Panel->System->Advanced->Environment Variables", and re-open the command window. '
                               'You only need to do it once'.format(install_dir))
        else:
            LOGGER.warning('Please ensure that %s is in your search PATH, so the `fzf` command can'
                           'be found.', install_dir)

    return os.path.expanduser(install_dir)


def _fzf_get_release(version):
    """
    Fetches the github release JSON blob for the given FZF version, or latest if not specified.
    """
    repos_url = 'https://api.github.com/repos/junegunn/fzf-bin/releases'

    LOGGER.info('Downloading fzf-bin releases JSON from "%s"', repos_url)
    try:
        releases = requests.get(repos_url).json()
    except OSError as error:
        raise CLIError(f'Connection error while attempting to download releases list: {error}') from error

    if version == 'latest':
        release = releases[0]
    else:
        release = next((r for r in releases if r["tag_name"] == version), None)

    if not release:
        raise CLIError(f'No release found for tag "{version}".')
    return release


def fzf_install(version='latest', install_dir=None):
    """
    Install fzf, a command line fuzzy finder.
    """

    arch = platform.machine()
    if arch == 'x86_64':
        arch = 'amd64'

    install_dir = _fzf_get_install_dir(install_dir)
    install_file = _fzf_get_filename()
    install_location = os.path.join(install_dir, install_file)

    release = _fzf_get_release(version)
    release_iter = (asset["browser_download_url"]
                    for asset
                    in release["assets"]
                    if _fzf_get_system().upper() in asset["name"].upper() and
                    arch.upper() in asset["name"].upper()
                    )
    file_url = next(release_iter, None)
    if not file_url:
        raise CLIError(f'No download found for {_fzf_get_system()} {arch}')

    LOGGER.info('Found download url "%s"', file_url)

    if not os.path.exists(install_dir):
        os.makedirs(install_dir)

    LOGGER.info('Downloading client to "%s" from "%s"', install_location, file_url)

    try:
        file_response = requests.get(file_url)
        compressed_file = io.BytesIO(file_response.content)
    except OSError as error:
        print("in except block")
        raise CLIError(f'Connection error while attempting to download client: {error}') from error

    if _fzf_get_system() == "Windows":
        with zipfile.ZipFile(compressed_file) as zip_file:
            zip_file.extract(install_file, path=install_dir)
    else:
        with tarfile.open(fileobj=compressed_file) as tar_file:
            tar_file.extract(install_file, path=install_dir)

    os.chmod(install_location,
             os.stat(install_location).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _fzf(items, **kwargs):
    """
    Calls the fzf finder with the correct arguments and input.

    Keyword arguments are available to override most FZF settings.

    # Search options
    exact (switch)
    case_insensitive (switch)
    case_sensitive (switch)
    nth (string)
    with_nth (string)
    delimiter (string)
    sort (switch)
    reverse_input (switch)
    tiebreak (string)

    # Interface options
    multi (switch)
    no_mouse (switch)
    cycle (switch)
    keep_right (switch)
    no_hscroll (switch)
    hscroll_off (string)
    filepath_word (switch)

    # Layout options
    layout (string)
    border (string)
    prompt (string)
    header (string)
    header_lines (integer)

    # Display
    ansi (switch)
    tabstop (string)
    color (string)
    no_bold (switch)

    # Preview
    preview (string)
    preview_window (string)

    # Scripting options
    query (string)
    select_1 (switch)
    exit_0 (switch)
    filter (string)
    print_query (switch)
    """

    # Find FZF. Check for get_config_dir() first, then fall back to system path.
    if shutil.which(_fzf_get_filename(), path=get_config_dir()):
        executable_path = shutil.which(_fzf_get_filename(), path=get_config_dir())
    else:
        executable_path = shutil.which(_fzf_get_filename(), path=os.environ.get('PATH'))
    if not executable_path:
        raise CLIError('Couldn\'t find fzf. You can install it via `az fzf install`.')
    LOGGER.info('Found fzf at %s.', executable_path)

    # Transformation between python function arguments and fzf command line arguments.
    fzf_arguments = {
        'exact': '--exact',
        'case_insensitive': '-i',
        'case_sensitive': '+i',
        'nth': '--nth={value}',
        'with_nth': '--with-nth={value}',
        'delimiter': '--delimiter={value}',
        'not sort': '--no-sort',
        'reverse_input': '--tac',
        'tiebreak': '--tiebreak={value}',
        'multi': '--multi',
        'no_mouse': '--no-mouse',
        'cycle': '--cycle',
        'keep_right': '--keep-right',
        'no_hscroll': '--no-hscroll',
        'hscroll_off': '--hscroll-off={value}',
        'filepath_word': '--filepath-word',
        'layout': '--layout={value}',
        'border': '--border={value}',
        'prompt': '--prompt={value}',
        'header': '--header={value}',
        'header_lines': '--header-lines={value}',
        'ansi': '--ansi',
        'tabstop': '--tabstop={value}',
        'color': '--color={value}',
        'no_bold': '--no-bold',
        'preview': '--preview={value}',
        'preview_window': '--preview-window={value}',
        'query': '--query={value}',
        'select_1': '--select-1',
        'exit_0': '--exit-0',
        'fzf_filter': '--filter={value}',
        'print_query': '--print-query'
    }

    # Build arguments list by iterating through kwargs.
    fzf_command = [executable_path]
    for key, value in kwargs.items():
        if value is not None:
            fzf_command.append(fzf_arguments[key].format(**locals()))
    LOGGER.info('fzf command: %s', " ".join(fzf_command))

    # Join the items array to a zero-delimited string for better handling
    # of embedded newlines and special characters
    items = "\0".join(items)
    fzf_command.append("--read0")

    # Open the process, then get the response back and return it.
    with subprocess.Popen(fzf_command, stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE, stderr=None) as fzf:
        stdout, _ = fzf.communicate(input=items.encode('UTF-8'))
    output = stdout.decode('UTF-8')
    LOGGER.info('fzf output: %s', output)
    return output


def _fzf_table(items, headers=None):
    """
    Produce a pretty table as an array of strings given headers and items.
    """
    return str(tabulate(items, headers=headers, tablefmt='github')).split('\n')


def fzf_group(cmd, fzf_filter=None, no_default=False):
    """
    Use fzf to quickly filter and select a default resource group.
    """
    from azure.cli.core.commands.parameters import get_resource_groups
    groups = get_resource_groups(cmd.cli_ctx)

    if not groups:
        raise CLIError('No resource groups found.'
                       'If you are logged in, make sure groups exist'
                       'and you have access to them. If you are not logged'
                       'in, please run "az login" to access your account.')

    # Use tabulate to make a pretty table for fzf to display
    headers = ["Name", "Location"]
    groups_sorted = sorted(groups, key=lambda i: i.name)
    groups_list = [[group.name, group.location] for group in groups_sorted]
    result = _fzf(_fzf_table(groups_list, headers), header_lines=2, fzf_filter=fzf_filter)

    if result:
        group = result.split('|')[1].strip()
        LOGGER.info('Selected group name: %s', group)
        if not no_default:
            cmd.cli_ctx.config.set_value(cmd.cli_ctx.config.defaults_section_name,
                                         'group', group)
        return next((g for g in groups if g.name == group), None)

    return None


def fzf_location(cmd, fzf_filter=None, no_default=False):
    """
    Use fzf to quickly filter and select a default location.
    """
    from azure.cli.core.commands.parameters import get_subscription_locations
    locations = get_subscription_locations(cmd.cli_ctx)

    if not locations:
        raise CLIError('No locations found.'
                       'If you are logged in, make sure a subscription exists'
                       'and you have access to it. If you are not logged'
                       'in, please run "az login" to access your account.')
    # Use tabulate to make a pretty table for fzf to display
    headers = ["Name", "Display Name", "Regional Display Name"]
    locations_sorted = sorted(locations, key=lambda i: i.name)
    locations_list = [[loc.name, loc.display_name, loc.regional_display_name] for loc in locations_sorted]
    result = _fzf(_fzf_table(locations_list, headers), header_lines=2, fzf_filter=fzf_filter)

    if result:
        location = result.split('|')[1].strip()
        if not no_default:
            cmd.cli_ctx.config.set_value(cmd.cli_ctx.config.defaults_section_name,
                                         'location', location)
        return next((loc for loc in locations if loc.name == location), None)

    return None


def fzf_subscription(cmd, fzf_filter=None, no_default=False):
    """
    Use fzf to quickly filter and select your current subscription.
    """
    from azure.cli.core._profile import Profile
    from azure.cli.core.api import load_subscriptions

    subscriptions = load_subscriptions(cmd.cli_ctx, all_clouds=False, refresh=False)

    if not subscriptions:
        raise CLIError('No subscriptions found.'
                       'If you are logged in, make sure subscriptions exist'
                       'and you have access to them. If you are not logged'
                       'in, please run "az login" to access your account.')
    headers = ["Name", "State", "ID"]
    subs_sorted = sorted(subscriptions, key=lambda i: i["name"])
    subs_list = [[sub["name"], sub["state"], sub["id"]] for sub in subs_sorted]
    result = _fzf(_fzf_table(subs_list, headers), header_lines=2, fzf_filter=fzf_filter)

    if result:
        subscription = result.split('|')[-2].strip()
        if not no_default:
            LOGGER.info('setting default subscription')
            Profile(cli_ctx=cmd.cli_ctx).set_active_subscription(subscription)
        return next((s for s in subscriptions if s["id"] == subscription))

    return None
