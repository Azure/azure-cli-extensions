# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import re
import json
from subprocess import check_output, check_call
from pkg_resources import parse_version


class AzdevExtension:
    def __init__(self, extension_name):
        self.name = extension_name

    @staticmethod
    def _cmd(cmd):
        check_call(cmd.split(), shell=True)

    def is_version_upgrade(self):
        with open('src/index.json') as fd:
            current_extensions = json.loads(fd.read()).get("extensions")

        metadata = current_extensions.get(self.name, None)
        if metadata is None:    # for new added extension
            return True

        current_max_entry = max(metadata, key=lambda e: parse_version(e['metadata']['version']))
        current_max_version = current_max_entry['metadata']['version']

        setup_py = 'src/{}/setup.py'.format(self.name)
        if os.path.isfile(setup_py):
            with open(setup_py) as fd:
                setup_py_content = fd.read()

            v = re.findall(r'VERSION = "(\d+.\d+.\d+)"', setup_py_content, re.S)
            if not v:
                raise Exception('version not found in {}'.format(setup_py))

            modified_version = v[0]
            if parse_version(current_max_version) > parse_version(modified_version):
                err = 'version downgrade is not allowed in extension {0}. [{1} -> {2}]'.format(setup_py,
                                                                                               current_max_version,
                                                                                               modified_version)
                raise Exception(err)
            if parse_version(current_max_version) == parse_version(modified_version):
                return False

        return True

    def build(self):
        """
        This default dist/ is placed at root dir
        """
        self._cmd('azdev extension build {}'.format(self.name))

    def upload(self):
        pass

    def update_index(self):
        pass


def find_modified_files_against_master_branch():
    """
    Deleted files don't count in diff
    """
    cmd = 'git --no-pager diff --diff-filter=ACMRT --name-only HEAD~1 -- src/'
    files = check_output(cmd.split()).decode('utf-8').split('\n')
    return [f for f in files if len(f) > 0]


def contain_extension_code(files):
    with open('src/index.json', 'r') as fd:
        current_extensions = json.loads(fd.read()).get("extensions")

    extensions_home_prefixes = set('src/{}'.format(name) for name in current_extensions)

    for file in files:
        if any([file.startswith(prefix) for prefix in extensions_home_prefixes]):
            return True

    return False


def main():
    modified_files = find_modified_files_against_master_branch()

    if 'src/index.json' in modified_files:
        modified_files.remove('src/index.json')

    if not contain_extension_code(modified_files):
        print('no extension source code is modified, no need to publish')

    extension_names = set()

    for f in modified_files:
        src, name, *_ = f.split('/')
        if os.path.isdir(os.path.join(src, name)):
            extension_names.add(name)

    for name in extension_names:
        azdev_extension = AzdevExtension(name)

        if azdev_extension.is_version_upgrade() is False:
            print('extension [{}] is not upgrade, no need to help publish'.format(name))
            continue

        azdev_extension.build()

        with open('./upgrade_extensions.txt', 'a') as fd:
            fd.write(name + '\n')


if __name__ == '__main__':
    main()
