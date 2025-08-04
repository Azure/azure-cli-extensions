# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import sys
import json
from subprocess import check_output
from pkg_resources import parse_version

def separator_line():
    print('-' * 100)

class AzdevExtensionHelper:
    def __init__(self, extension_name):
        self.name = extension_name

    def _get_metadata_flags(self, setup_py_dir):
        for root, _, files in os.walk(setup_py_dir):
            if 'azext_metadata.json' in files:
                metadata_path = os.path.join(root, 'azext_metadata.json')
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    is_experimental = metadata.get('azext.isExperimental', False)
                    is_preview = metadata.get('azext.isPreview', False)
                return is_experimental, is_preview
        return False, False

    def _adjust_version_for_preview(self, version, setup_py_dir):
        is_experimental, is_preview = self._get_metadata_flags(setup_py_dir)
        if is_experimental or is_preview:
            version_parts = version.split('.')
            if all(part.isdigit() for part in version_parts):
                version = f"{version}b1"
        return version

    def is_version_upgrade(self):
        with open('src/index.json') as fd:
            current_extensions = json.loads(fd.read()).get("extensions")

        setup_py = f'src/{self.name}/setup.py'
        if not os.path.isfile(setup_py):
            print('no setup.py')
            return False

        setup_py_dir = os.path.dirname(setup_py)
        cmd = f'{sys.executable} setup.py --name'
        self.name = check_output(cmd, shell=True, cwd=setup_py_dir).decode('utf-8').strip()
        self.name = self.name.replace('_', '-')

        metadata = current_extensions.get(self.name, None)
        if metadata is None:    # for new added extension
            return True

        current_max_entry = max(metadata, key=lambda e: parse_version(e['metadata']['version']))
        current_max_version = current_max_entry['metadata']['version']
        current_max_version = self._adjust_version_for_preview(current_max_version, setup_py_dir)
        print(f'current max version is {current_max_version}')

        cmd = f'{sys.executable} setup.py --version'
        modified_version = check_output(cmd, shell=True, cwd=setup_py_dir).decode('utf-8').strip()
        print(f'modified version is {modified_version}')

        if parse_version(current_max_version) > parse_version(modified_version):
            err = f'version downgrade is not allowed in extension {setup_py}. [{current_max_version} -> {modified_version}]'
            raise Exception(err)

        if parse_version(current_max_version) == parse_version(modified_version):
            return False

        return True

def find_modified_files_against_master_branch():
    """
    Deleted files don't count in diff
    """
    cmd = 'git --no-pager diff --diff-filter=ACMRT --name-only HEAD~1 -- src/'
    files = check_output(cmd.split()).decode('utf-8').split('\n')
    separator_line()
    print('modified files:')
    for f in files:
        print(f)
    separator_line()
    return [f for f in files if len(f) > 0]

def contain_extension_code(files):
    with open('src/index.json', 'r') as fd:
        current_extensions = json.loads(fd.read()).get("extensions")
    current_extension_homes = set(f'src/{name}' for name in current_extensions)

    for file in files:
        if any([file.startswith(prefix) for prefix in current_extension_homes]):
            return True

    # for new added extensions or modules that src folder name does not match its wheel package name
    for file in files:
        if 'src/' in file and os.path.isfile(file) and os.path.isdir(os.path.dirname(file)):
            new_extension_home = os.path.dirname(file)
            new_extension_home = os.path.join(*new_extension_home.split('/')[:2])
            if os.path.isfile(os.path.join(new_extension_home, 'setup.py')):
                return True
    return False

def main():
    modified_files = find_modified_files_against_master_branch()
    if 'src/index.json' in modified_files:
        modified_files.remove('src/index.json')

    # check setup.py
    for f in modified_files:
        if f.endswith('setup.py'):
            break
    else:
        separator_line()
        print('no setup.py is modified, no need to publish')
        separator_line()
        return

    # check source code
    if not contain_extension_code(modified_files):
        separator_line()
        print('no extension source code is modified, no need to publish')
        separator_line()
        return

    extension_names = set()
    for f in modified_files:
        src, name, *_ = f.split('/')
        if os.path.isdir(os.path.join(src, name)):
            extension_names.add(name)

    for name in extension_names:
        azdev_extension = AzdevExtensionHelper(name)
        if azdev_extension.is_version_upgrade() is False:
            print(f'extension [{name}] is not upgrade, no need to help publish')
            continue
        with open('./upgrade_extensions.txt', 'a') as fd:
            fd.write(name + '\n')

if __name__ == '__main__':
    main()
