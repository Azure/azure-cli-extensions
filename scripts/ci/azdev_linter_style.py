# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
This script is used to run azdev linter and azdev style on extensions.

It's only working on ADO by default. If want to run locally,
please update the target branch/commit to find diff in function find_modified_files_against_master_branch()
"""
import json
import logging
import os
import re
import shutil
from subprocess import CalledProcessError, check_call, check_output

import service_name
from pkg_resources import parse_version
from util import get_ext_metadata

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

def separator_line():
    logger.info('-' * 100)


class ModifiedFilesNotAllowedError(Exception):
    """
    Exception raise for the scenario that modified files is conflict against publish requirement.
    Scenario 1: if modified files contain only src/index.json, don't raise
    Scenario 2: if modified files contain not only extension code but also src/index.json, raise.
    Scenario 3: if modified files don't contain src/index.json, don't raise.
    """

    def __str__(self):
        msg = """
        ---------------------------------------------------------------------------------------------------------
        You have modified both source code and src/index.json!

        There is a release pipeline will help you to build, upload and publish your extension.
        Once your PR is merged into master branch, a new PR will be created to update src/index.json automatically.

        If you want us to help to build, upload and publish your extension, src/index.json must not be modified.
        ---------------------------------------------------------------------------------------------------------
        """
        return msg


class AzExtensionHelper:
    def __init__(self, extension_name):
        self.extension_name = extension_name

    @staticmethod
    def _cmd(cmd):
        logger.info(cmd)
        check_call(cmd, shell=True)

    def add_from_url(self, url):
        self._cmd('az extension add -s {} -y'.format(url))

    def remove(self):
        self._cmd('az extension remove -n {}'.format(self.extension_name))


class AzdevExtensionHelper:
    def __init__(self, extension_name):
        self.extension_name = extension_name

    @staticmethod
    def _cmd(cmd):
        logger.info(cmd)
        check_call(cmd, shell=True)

    def add_from_code(self):
        self._cmd('azdev extension add {}'.format(self.extension_name))

    def remove(self):
        self._cmd('azdev extension remove {}'.format(self.extension_name))

    def linter(self):
        self._cmd('azdev linter --include-whl-extensions {}'.format(self.extension_name))

    def style(self):
        self._cmd('azdev style {}'.format(self.extension_name))

    def build(self):
        self._cmd('azdev extension build {}'.format(self.extension_name))

    def check_extension_name(self):
        extension_root_dir_name = self.extension_name
        original_cwd = os.getcwd()
        dist_dir = os.path.join(original_cwd, 'dist')
        files = os.listdir(dist_dir)
        logger.info(f"wheel files in the dist directory: {files}")
        for f in files:
            if f.endswith('.whl'):
                NAME_REGEX = r'(.*)-\d+.\d+.\d+'
                extension_name = re.findall(NAME_REGEX, f)[0]
                extension_name = extension_name.replace('_', '-')
                logger.info(f"extension name is: {extension_name}")
                ext_file = os.path.join(dist_dir, f)
                break
        metadata = get_ext_metadata(dist_dir, ext_file, extension_name)
        pretty_metadata = json.dumps(metadata, indent=2)
        logger.info(f"metadata in the wheel file is: {pretty_metadata}")
        shutil.rmtree(dist_dir)
        if '_' in extension_root_dir_name:
            raise ValueError(f"Underscores `_` are not allowed in the extension root directory, "
                             f"please change it to a hyphen `-`.")
        if metadata['name'] != extension_name:
            raise ValueError(f"The name {metadata['name']} in setup.py "
                             f"is not the same as the extension name {extension_name}! \n"
                             f"Please fix the name in setup.py!")


def find_modified_files_against_master_branch():
    """
    Find modified files from src/ only.
    A: Added, C: Copied, M: Modified, R: Renamed, T: File type changed.
    Deleted files don't count in diff.
    """
    ado_pr_target_branch = 'origin/' + os.environ.get('ADO_PULL_REQUEST_TARGET_BRANCH')

    separator_line()
    logger.info('pull request target branch: %s', ado_pr_target_branch)

    cmd = 'git --no-pager diff --name-only --diff-filter=ACMRT {} -- src/'.format(ado_pr_target_branch)
    files = check_output(cmd.split()).decode('utf-8').split('\n')
    files = [f for f in files if len(f) > 0]

    if files:
        logger.info('modified files:')
        separator_line()
        for f in files:
            logger.info(f)

    return files


def contain_index_json(files):
    return 'src/index.json' in files


def contain_extension_code(files):
    with open('src/index.json', 'r') as fd:
        current_extensions = json.loads(fd.read()).get("extensions")

    current_extension_homes = set('src/{}'.format(name) for name in current_extensions)

    for file in files:
        if any([file.startswith(prefix) for prefix in current_extension_homes]):
            return True

    # for new added extensions
    for file in files:
        if 'src/' in file and os.path.isfile(file) and os.path.isdir(os.path.dirname(file)):
            new_extension_home = os.path.dirname(file)

            if os.path.isfile(os.path.join(new_extension_home, 'setup.py')):
                return True

    return False


def azdev_on_external_extension(index_json, azdev_type):
    """
    Check if the modified metadata items in index.json refer to the extension in repo.
    If not, az extension check on wheel. Otherwise skip it.
    """

    public_extensions = json.loads(check_output('az extension list-available -d', shell=True))

    with open(index_json, 'r') as fd:
        current_extensions = json.loads(fd.read()).get("extensions")

    for name in current_extensions:
        modified_entries = [entry for entry in current_extensions[name] if entry not in public_extensions.get(name, [])]

        if not modified_entries:
            continue

        # check if source code exists, if so, skip
        if os.path.isdir('src/{}'.format(name)):
            continue

        separator_line()

        latest_entry = max(modified_entries, key=lambda c: parse_version(c['metadata']['version']))

        az_extension = AzExtensionHelper(name)
        az_extension.add_from_url(latest_entry['downloadUrl'])

        azdev_extension = AzdevExtensionHelper(name)
        if azdev_type in ['all', 'linter']:
            azdev_extension.linter()
        # TODO:
        # azdev style support external extension
        # azdev test support external extension
        # azdev_extension.style()

        logger.info('Checking service name for external extensions')
        service_name.check()

        az_extension.remove()


def azdev_on_internal_extension(modified_files, azdev_type):
    extension_names = set()

    for f in modified_files:
        src, name, *_ = f.split('/')
        if os.path.isdir(os.path.join(src, name)):
            extension_names.add(name)

    if not extension_names:
        separator_line()
        logger.info('no extension source code modified, no extension needs to be checked')

    for name in extension_names:
        separator_line()

        azdev_extension = AzdevExtensionHelper(name)
        azdev_extension.add_from_code()
        if azdev_type in ['all', 'linter']:
            azdev_extension.linter()
            azdev_extension.build()
            azdev_extension.check_extension_name()
        if azdev_type in ['all', 'style']:
            try:
                azdev_extension.style()
            except CalledProcessError as e:
                statement_msg = """
                ------------------- Please note -------------------
                This task does not block the PR merge.
                And it is recommended if you want to create a separate PR to fix these style issues.
                CLI will modify it to force block PR merge on 2025.
                ---------------------- Thanks ----------------------
                """
                logger.error(statement_msg)
                exit(1)

        logger.info('Checking service name for internal extensions')
        service_name.check()

        azdev_extension.remove()


def main():
    import argparse
    parser = argparse.ArgumentParser(description='azdev linter and azdev style on modified extensions')
    parser.add_argument('--type',
                        type=str,
                        help='Control whether azdev linter, azdev style, azdev test needs to be run. '
                             'Supported values: linter, style, test, all, all is the default.', default='all')
    args = parser.parse_args()
    azdev_type = args.type
    logger.info('azdev type: %s', azdev_type)
    modified_files = find_modified_files_against_master_branch()

    if len(modified_files) == 1 and contain_index_json(modified_files):
        # Scenario 1.
        # This scenarios is for modify index.json only.
        # If the modified metadata items refer to the extension code exits in this repo, PR is be created via Pipeline.
        # If the modified metadata items refer to the extension code doesn't exist, PR is created from Service Team.
        # We try to run azdev linter and azdev style on it.
        azdev_on_external_extension(modified_files[0], azdev_type)
    else:
        # modified files contain more than one file

        if contain_extension_code(modified_files):
            # Scenario 2, we reject.
            if contain_index_json(modified_files):
                raise ModifiedFilesNotAllowedError()

            azdev_on_internal_extension(modified_files, azdev_type)
        else:
            separator_line()
            logger.info('no extension source code modified, no extension needs to be checked')
            separator_line()


if __name__ == '__main__':
    try:
        main()
    except ModifiedFilesNotAllowedError as e:
        logger.error(e)
        exit(1)
