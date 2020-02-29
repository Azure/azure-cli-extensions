#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from subprocess import check_output

CONTEXT = """
This script is used to detect requirements for publish.
If your want us to help to build, upload and publish extension wheel, src/index.json must not be modified.
A release pipeline will help to do it once PR is merged and and a Pull Request will be created to update src/index.json.
The precondition is to put your source code inside repo Azure/azure-cli-extensions, cause we must build on source code.

If your source code is outside of this repo, you have to build, upload and publish by yourself.
"""


class ModifiedFilesNotAllow(Exception):
    """
    Exception raise for the scenario that modified files is conflict against publish requirement.
    Scenario 1: if modified files contain only src/index.json, don't raise
    Scenario 2: if modified files contain not only extension code but also src/index.json, raise.
    Scenario 3: if modified files don't contain src/index.json, don't raise.
    """


def find_modified_files_against_master_branch():
    cmd = 'git --no-pager diff --name-only origin/master -- src/'
    return check_output(cmd.split())


def contain_index_json(files):
    return 'src/index.json' in files


def contain_extension_code(files):
    for file in files:
        if os.path.isdir(file) and 'setup.py' in os.listdir(file):
            return True

    return False


def main():
    modified_files = find_modified_files_against_master_branch()

    if len(modified_files) == 1 and contain_index_json(modified_files):
        # Scenario 1.
        # This scenarios is for modify index.json only.
        # If the modified metadata items refer to the extension code exits in this repo, PR is be created via Pipeline.
        # If the modified metadata items refer to the extension code doesn't exist, PR is created from Service Team.
        # We allow.
        pass
    else:
        # modified files contain more than one file

        if contain_extension_code(modified_files) and contain_index_json(modified_files):
            # Scenario 2, we reject.
            raise ModifiedFilesNotAllow(CONTEXT)

        # other scenarios, we allow.
        print('Precheck is fine. We are able to help to build and upload.')


if __name__ == '__main__':
    try:
        main()
    except ModifiedFilesNotAllow as e:
        print(e)
