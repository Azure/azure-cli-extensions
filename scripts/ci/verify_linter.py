# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
This script is used to verify linter on extensions.

It's only working on ADO by default. If want to run locally,
please update the target branch/commit to find diff in function find_modified_files_against_master_branch()
"""

import os
import json
from subprocess import check_output, check_call
from pkg_resources import parse_version


def separator_line():
    print('-' * 100)


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
        print(cmd)
        check_call(cmd.split(), shell=True)

    def add_from_url(self, url):
        self._cmd('az extension add -s {} -y'.format(url))

    def remove(self):
        self._cmd('az extension remove -n {}'.format(self.extension_name))


class AzdevExtensionHelper:
    def __init__(self, extension_name):
        self.extension_name = extension_name

    @staticmethod
    def _cmd(cmd):
        print(cmd)
        check_call(cmd, shell=True)

    def add_from_code(self):
        self._cmd('azdev extension add {}'.format(self.extension_name))

    def remove(self):
        self._cmd('azdev extension remove {}'.format(self.extension_name))

    def linter(self):
        self._cmd('azdev linter --include-whl-extensions {}'.format(self.extension_name))

    def build(self):
        pass


def find_modified_files_against_master_branch():
    """
    Find modified files from src/ only.
    A: Added, C: Copied, M: Modified, R: Renamed, T: File type changed.
    Deleted files don't count in diff.
    """
    ado_pr_target_branch = 'origin/' + os.environ.get('ADO_PULL_REQUEST_TARGET_BRANCH')

    separator_line()
    print('pull request target branch:', ado_pr_target_branch)

    cmd = 'git --no-pager diff --name-only --diff-filter=ACMRT {} -- src/'.format(ado_pr_target_branch)
    files = check_output(cmd.split()).decode('utf-8').split('\n')
    files = [f for f in files if len(f) > 0]

    if files:
        separator_line()
        for f in files:
            print(f)

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


def linter_on_external_extension(index_json):
    """
    Check if the modified metadata items in index.json refer to the extension in repo.
    If not, az extension linter on wheel. Otherwise skip it.
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
        azdev_extension.linter()

        az_extension.remove()


def linter_on_internal_extension(modified_files):
    extension_names = set()

    for f in modified_files:
        src, name, *_ = f.split('/')
        if os.path.isdir(os.path.join(src, name)):
            extension_names.add(name)

    if not extension_names:
        separator_line()
        print('no extension source code modified, no extension needs to be linter')

    for name in extension_names:
        separator_line()

        azdev_extension = AzdevExtensionHelper(name)
        azdev_extension.add_from_code()
        azdev_extension.linter()
        azdev_extension.remove()


def main():
    modified_files = find_modified_files_against_master_branch()

    if len(modified_files) == 1 and contain_index_json(modified_files):
        # Scenario 1.
        # This scenarios is for modify index.json only.
        # If the modified metadata items refer to the extension code exits in this repo, PR is be created via Pipeline.
        # If the modified metadata items refer to the extension code doesn't exist, PR is created from Service Team.
        # We try to verify linter on it.
        linter_on_external_extension(modified_files[0])
    else:
        # modified files contain more than one file

        if contain_extension_code(modified_files):
            # Scenario 2, we reject.
            if contain_index_json(modified_files):
                raise ModifiedFilesNotAllowedError()

            linter_on_internal_extension(modified_files)
        else:
            separator_line()
            print('no extension source code modified, no extension needs to be linter')
            separator_line()


if __name__ == '__main__':
    try:
        main()
    except ModifiedFilesNotAllowedError as e:
        print(e)
        exit(1)
