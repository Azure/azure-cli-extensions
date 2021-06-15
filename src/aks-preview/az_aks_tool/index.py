# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import glob
import logging
import os
from importlib import import_module

import az_aks_tool.utils as utils
import az_aks_tool.const as const
logger = logging.getLogger(__name__)


def get_repo_path(repo_name, root_path=None):
    # find cache from environment variable
    repo_path = os.environ.get("{}_PATH".format(repo_name), "")
    if os.path.isdir(repo_path):
        logger.info("Find cached '{}' repo path: '{}'".format(repo_name, repo_path))
        return repo_path

    # search from root_path
    candidate_root_paths = [os.getcwd(), os.path.expanduser("~")]
    valid_repo_paths = []
    repo_path = ""
    if root_path is None or not os.path.isdir(root_path):
        logger.warning("Invalid root path '{}'!".format(root_path))
    else:
        candidate_root_paths = [root_path] + candidate_root_paths
    logger.info("Setting root path from '{}'".format(candidate_root_paths))
    for candidate_root_path in candidate_root_paths:
        root_path = candidate_root_path
        logger.info("Searching from root path: '{}'".format(root_path))
        for path, _, _ in os.walk(root_path):
            pattern = os.path.join(path, repo_name)
            valid_repo_paths.extend(glob.glob(pattern))
        if len(valid_repo_paths) >= 1:
            repo_path = valid_repo_paths[0]
            if len(valid_repo_paths) >= 2:
                logger.warning("Find {} '{}' repo paths: {}".format(len(valid_repo_paths), repo_name, valid_repo_paths))
            logger.info("Set '{}' repo path as '{}'".format(repo_name, repo_path))
            os.environ["{}_PATH".format(repo_name)] = str(repo_path)
            return repo_path
        else:
            logger.warning("Could not find valid path to repo '{}' from '{}'".format(repo_name, root_path))
    return repo_path

def find_files(root_paths, file_pattern):
    """ Returns the paths to all files that match a given pattern.

    :returns: Paths ([str]) to files matching the given pattern.
    """
    if isinstance(root_paths, str):
        root_paths = [root_paths]
    paths = []
    for root_path in root_paths:
        for path, _, _ in os.walk(root_path):
            pattern = os.path.join(path, file_pattern)
            paths.extend(glob.glob(pattern))
    return paths

def get_name_index(invert=False, include_whl_extensions=False):
    """ Returns a dictionary containing the long and short names of modules and extensions is {SHORT:LONG} format or
        {LONG:SHORT} format when invert=True. """
    from azure.cli.core.extension import EXTENSIONS_DIR  # pylint: disable=import-error

    table = {}
    cli_repo_path = get_repo_path(const.CLI_REPO_NAME)
    ext_repo_paths = get_repo_path(const.EXT_REPO_NAME)

    # unified azure-cli package (2.0.68 and later)
    paths = os.path.normcase(
        os.path.join(
            cli_repo_path, 'src', 'azure-cli', 'azure', 'cli', 'command_modules', '*', '__init__.py'
        )
    )
    modules_paths = glob.glob(paths)
    core_paths = glob.glob(os.path.normcase(os.path.join(cli_repo_path, 'src', '*', 'setup.py')))
    ext_paths = [x for x in find_files(ext_repo_paths, '*.*-info') if 'site-packages' not in x]
    whl_ext_paths = []
    if include_whl_extensions:
        whl_ext_paths = [x for x in find_files(EXTENSIONS_DIR, '*.*-info') if 'site-packages' not in x]

    def _update_table(paths, key):
        folder = None
        long_name = None
        short_name = None
        for path in paths:
            folder = os.path.dirname(path)
            base_name = os.path.basename(folder)
            # determine long-names
            if key == 'ext':
                short_name = base_name
                for item in os.listdir(folder):
                    if item.startswith(const.EXTENSION_PREFIX):
                        long_name = item
                        break
            elif base_name.startswith(const.COMMAND_MODULE_PREFIX):
                long_name = base_name
                short_name = base_name.replace(const.COMMAND_MODULE_PREFIX, '') or '__main__'
            else:
                short_name = base_name
                long_name = '{}{}'.format(const.COMMAND_MODULE_PREFIX, base_name)
            if not invert:
                table[short_name] = long_name
            else:
                table[long_name] = short_name

    _update_table(modules_paths, 'mod')
    _update_table(core_paths, 'core')
    _update_table(ext_paths, 'ext')
    _update_table(whl_ext_paths, 'ext')

    return table

# pylint: disable=too-many-statements
def get_path_table(include_only=None, include_whl_extensions=False):
    """ Returns a table containing the long and short names of different modules and extensions and the path to them.
        The structure looks like:
    {
        'core': {
            NAME: PATH,
            ...
        },
        'mod': {
            NAME: PATH,
            ...
        },
        'ext': {
            NAME: PATH,
            ...
        }
    }
    """
    from azure.cli.core.extension import EXTENSIONS_DIR  # pylint: disable=import-error

    # determine whether the call will filter or return all
    if isinstance(include_only, str):
        include_only = [include_only]
    get_all = not include_only

    table = {}
    cli_repo_path = get_repo_path(const.CLI_REPO_NAME)
    ext_repo_paths = get_repo_path(const.EXT_REPO_NAME)

    paths = os.path.normcase(
        os.path.join(
            cli_repo_path, 'src', 'azure-cli', 'azure', 'cli', 'command_modules', '*', '__init__.py'
        )
    )
    modules_paths = glob.glob(paths)
    core_paths = glob.glob(os.path.normcase(os.path.join(cli_repo_path, 'src', '*', 'setup.py')))
    ext_paths = [x for x in find_files(ext_repo_paths, '*.*-info') if 'site-packages' not in x]
    whl_ext_paths = [x for x in find_files(EXTENSIONS_DIR, '*.*-info') if 'site-packages' not in x]

    def _update_table(package_paths, key):
        if key not in table:
            table[key] = {}

        for path in package_paths:
            folder = os.path.dirname(path)
            base_name = os.path.basename(folder)

            if key == 'ext':
                short_name = base_name
                long_name = next((item for item in os.listdir(folder) if item.startswith(const.EXTENSION_PREFIX)), None)
            else:
                short_name = base_name
                long_name = '{}{}'.format(const.COMMAND_MODULE_PREFIX, base_name)

            if get_all:
                table[key][long_name if key == 'ext' else short_name] = folder
            elif not include_only:
                return  # nothing left to filter
            else:
                # check and update filter
                if short_name in include_only:
                    include_only.remove(short_name)
                    table[key][short_name] = folder
                if long_name in include_only:
                    # long name takes precedence to ensure path doesn't appear twice
                    include_only.remove(long_name)
                    table[key].pop(short_name, None)
                    table[key][long_name] = folder

    _update_table(modules_paths, 'mod')
    _update_table(core_paths, 'core')
    _update_table(ext_paths, 'ext')
    if include_whl_extensions:
        _update_table(whl_ext_paths, 'ext')

    if include_only:
        whl_extensions = [mod for whl_ext_path in whl_ext_paths for mod in include_only if mod in whl_ext_path]
        if whl_extensions:
            err = 'extension(s): [ {} ] installed from a wheel may need --include-whl-extensions option'.format(
                ', '.join(whl_extensions))
            raise Exception(err)

        raise Exception('unrecognized modules: [ {} ]'.format(', '.join(include_only)))

    return table

def discover_module_tests(mod_name, mod_data):

    # get the list of test files in each module
    total_tests = 0
    total_files = 0
    logger.info('Mod: %s', mod_name)
    try:
        contents = os.listdir(mod_data['filepath'])
        test_files = {
            x[:-len('.py')]: {} for x in contents if x.startswith('test_') and x.endswith('.py')
        }
        total_files = len(test_files)
    except FileNotFoundError:
        logger.info('  No test files found.')
        return None

    for file_name in test_files:
        mod_data['files'][file_name] = {}
        test_file_path = mod_data['base_path'] + '.' + file_name
        try:
            module = import_module(test_file_path)
        except ImportError as ex:
            logger.info('    %s', ex)
            continue
        module_dict = module.__dict__
        possible_test_classes = {x: y for x, y in module_dict.items() if not x.startswith('_')}
        for class_name, class_def in possible_test_classes.items():
            try:
                class_dict = class_def.__dict__
            except AttributeError:
                # skip non-class symbols in files like constants, imported methods, etc.
                continue
            if class_dict.get('__module__') == test_file_path:
                tests = [x for x in class_def.__dict__ if x.startswith('test_')]
                if tests:
                    mod_data['files'][file_name][class_name] = tests
                total_tests += len(tests)
    logger.info('  %s tests found in %s files.', total_tests, total_files)
    return mod_data


def build_test_index(module_data):
    test_index = {}
    conflicted_keys = []

    def add_to_index(key, path):
        key = key or mod_name
        if key in test_index:
            if key not in conflicted_keys:
                conflicted_keys.append(key)
            mod1 = utils.extract_module_name(path)
            mod2 = utils.extract_module_name(test_index[key])
            if mod1 != mod2:
                # resolve conflicted keys by prefixing with the module name and a dot (.)
                logger.warning("'%s' exists in both '%s' and '%s'. Resolve using `%s.%s` or `%s.%s`",
                               key, mod1, mod2, mod1, key, mod2, key)
                test_index['{}.{}'.format(mod1, key)] = path
                test_index['{}.{}'.format(mod2, key)] = test_index[key]
            else:
                logger.error("'%s' exists twice in the '%s' module", key, mod1)
        else:
            test_index[key] = path

    # build the index
    for mod_name, mod_data in module_data.items():
        # don't add empty mods to the index
        if not mod_data:
            continue

        mod_path = mod_data['filepath']
        for file_name, file_data in mod_data['files'].items():
            file_path = os.path.join(mod_path, file_name) + '.py'
            for class_name, test_list in file_data.items():
                for test_name in test_list:
                    test_path = '{}::{}::{}'.format(file_path, class_name, test_name)
                    add_to_index(test_name, test_path)
                class_path = '{}::{}'.format(file_path, class_name)
                add_to_index(class_name, class_path)
            add_to_index(file_name, file_path)
        add_to_index(mod_name, mod_path)
        add_to_index(mod_data['alt_name'], mod_path)

    # remove the conflicted keys since they would arbitrarily point to a random implementation
    for key in conflicted_keys:
        del test_index[key]

    return test_index
