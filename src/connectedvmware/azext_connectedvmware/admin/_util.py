# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This module is wrapper around az cli command execution
# az_cli and az_cli_with_retries are two functions which
# can be used to execute az commands.

import subprocess, logging
from functools import total_ordering


def bytes_to_string(b: bytes) -> str:
    return b.decode('UTF-8', errors='strict')

def az_cli (*args):
    res = None
    try:
        cmd = 'az ' + ' '.join(args)
        # logging.debug(f'Executing command {cmd}')
        try:
            res = subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError as e:
            logging.error(bytes_to_string(e.output))
            return res, 1
        res = bytes_to_string(res)
    except Exception as e:
        logging.exception(e)
        return res, 1
    return res, 0


@total_ordering
class SemanticVersion:
    def __init__(self, version_string):
        self.version_string = version_string
        self.version = [int(v) for v in version_string.split('.')]

    def __repr__(self):
        return f"SemanticVersion('{self.version_string}')"

    def __eq__(self, other):
        if not isinstance(other, SemanticVersion):
            return NotImplemented
        return self.version == other.version

    def __lt__(self, other):
        if not isinstance(other, SemanticVersion):
            return NotImplemented
        return self.version < other.version
