# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import errno
import os
import platform
import stat
import tempfile

import yaml
from azure.cli.core.azclierror import FileOperationError
from knack.log import get_logger
from knack.prompting import NoTTYException, prompt_y_n
from knack.util import CLIError

logger = get_logger(__name__)


def parse_key_value_list(pairs):
    """Parse a list of ``key=value`` strings into a dictionary."""
    result = {}
    if pairs is None:
        return result
    for pair in pairs:
        if "=" not in pair:
            raise CLIError(f"Invalid format '{pair}'. Expected format key=value.")
        key, value = pair.split("=", 1)
        result[key.strip()] = value.strip()
    return result


def get_aks_custom_headers(aks_custom_headers=None):
    """Parse a comma separated ``key=value`` string into a request headers dictionary."""
    headers = {}
    if aks_custom_headers is not None:
        if aks_custom_headers != "":
            for pair in aks_custom_headers.split(','):
                parts = pair.split('=')
                if len(parts) != 2:
                    raise CLIError('custom headers format is incorrect')
                headers[parts[0]] = parts[1]
    return headers


def print_or_merge_credentials(path, kubeconfig, overwrite_existing, context_name):
    """Merge an unencrypted kubeconfig into the file at the specified path, or print it to
    stdout if the path is "-".
    """
    # Special case for printing to stdout
    if path == "-":
        print(kubeconfig)
        return

    # ensure that at least an empty ~/.kube/config exists
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError as ex:
            if ex.errno != errno.EEXIST:
                raise
    if not os.path.exists(path):
        with os.fdopen(os.open(path, os.O_CREAT | os.O_WRONLY, 0o600), 'wt'):
            pass

    # merge the new kubeconfig into the existing one
    fd, temp_path = tempfile.mkstemp()
    additional_file = os.fdopen(fd, 'w+t')
    try:
        additional_file.write(kubeconfig)
        additional_file.flush()
        _merge_kubernetes_configurations(path, temp_path, overwrite_existing, context_name)
    except yaml.YAMLError as ex:
        logger.warning('Failed to merge credentials to kube config file: %s', ex)
    finally:
        additional_file.close()
        os.remove(temp_path)


def _merge_kubernetes_configurations(existing_file, addition_file, replace, context_name=None):
    existing = _load_kubernetes_configuration(existing_file)
    addition = _load_kubernetes_configuration(addition_file)

    if addition is None:
        raise CLIError(f'failed to load additional configuration from {addition_file}')

    if context_name is not None:
        addition['contexts'][0]['name'] = context_name
        addition['contexts'][0]['context']['cluster'] = context_name
        addition['clusters'][0]['name'] = context_name
        addition['current-context'] = context_name

    # rename the admin context so it doesn't overwrite the user context
    for ctx in addition.get('contexts', []):
        try:
            if ctx['context']['user'].startswith('clusterAdmin'):
                admin_name = ctx['name'] + '-admin'
                addition['current-context'] = ctx['name'] = admin_name
                break
        except (KeyError, TypeError):
            continue

    if existing is None:
        existing = addition
    else:
        _handle_merge(existing, addition, 'clusters', replace)
        _handle_merge(existing, addition, 'users', replace)
        _handle_merge(existing, addition, 'contexts', replace)
        existing['current-context'] = addition['current-context']

    # check that ~/.kube/config is only read- and writable by its owner
    if platform.system() != "Windows" and not os.path.islink(existing_file):
        existing_file_perms = f"{stat.S_IMODE(os.lstat(existing_file).st_mode):o}"
        if not existing_file_perms.endswith("600"):
            logger.warning(
                '%s has permissions "%s".\nIt should be readable and writable only by its owner.',
                existing_file,
                existing_file_perms,
            )

    with open(existing_file, 'w+', encoding="utf-8") as stream:
        yaml.safe_dump(existing, stream, default_flow_style=False)

    current_context = addition.get('current-context', 'UNKNOWN')
    logger.warning('Merged "%s" as current context in %s', current_context, existing_file)


def _load_kubernetes_configuration(filename):
    try:
        with open(filename, encoding="utf-8") as stream:
            return yaml.safe_load(stream)
    except (IOError, OSError) as ex:
        if getattr(ex, 'errno', 0) == errno.ENOENT:
            raise CLIError(f'{filename} does not exist') from ex
        raise
    except (yaml.parser.ParserError, UnicodeDecodeError) as ex:
        raise CLIError(f'Error parsing {filename} ({str(ex)})') from ex


def _handle_merge(existing, addition, key, replace):
    if not addition.get(key, False):
        return
    if key not in existing:
        raise FileOperationError(
            f"No such key '{key}' in existing config, please confirm whether it is a valid config file. "
            "May back up this config file, delete it and retry the command."
        )
    if not existing.get(key):
        existing[key] = addition[key]
        return

    for i in addition[key]:
        for j in existing[key]:
            if not i.get('name', False) or not j.get('name', False):
                continue
            if i['name'] == j['name']:
                if replace or i == j:
                    existing[key].remove(j)
                else:
                    overwrite = False
                    try:
                        overwrite = prompt_y_n(
                            f'A different object named {i["name"]} already exists in your kubeconfig file.\nOverwrite?')
                    except NoTTYException:
                        pass
                    if overwrite:
                        existing[key].remove(j)
                    else:
                        raise CLIError(
                            f'A different object named {i["name"]} already exists in {key} in your kubeconfig file.')
        existing[key].append(i)
