# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This module is wrapper around az cli command execution
# az_cli and az_cli_with_retries are two functions which
# can be used to execute az commands.

import subprocess, logging
from functools import total_ordering
from typing import List, Union, Tuple

# https://github.com/Azure/iotedgedev/blob/4e51ecdcddd4bdd565312dc72401701a202b4e3f/iotedgedev/azurecli.py#L48
class AzCli:
    def __init__(self, logfile: Union[str, None]=None) -> None:
        self.logfile = logfile
        self.logger = new_logger(logfile=self.logfile)

    def run(self, *args, capture_output = True) -> Tuple[str, int]:
        stdout_data = b''
        f = None
        return_code = 1
        try:
            cmd = ['az'] + list(args)
            self.logger.debug("Running az command: %s", list(args))
            if not capture_output:
                process = subprocess.Popen(
                    cmd,
                )
                return_code = process.wait()
            else:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                for line in process.stderr:
                    if self.logfile is not None:
                        with open(self.logfile, 'ab') as f:
                            f.write(line)
                for line in process.stdout:
                    if self.logfile is not None:
                        with open(self.logfile, 'ab') as f:
                            f.write(line)
                    stdout_data += line
                return_code = process.wait()
        except Exception as e:
            if self.logfile is not None:
                with open(self.logfile, 'ab') as f:
                    f.write(bytes_to_string(str(e)))
            return "", return_code
        res = bytes_to_string(stdout_data)
        return res, return_code

def bytes_to_string(b: bytes) -> str:
    return b.decode('UTF-8', errors='strict')


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


def new_logger(
        name: Union[str, None]=None,
        logfile: Union[str, None]=None,
        handlers: Union[List[logging.Handler], None] = None
    ) -> logging.Logger:
    name = name or __name__
    logger = logging.getLogger(name)
    formatter = logging.Formatter(
        fmt='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S',
    )
    if not handlers:
        if logfile is not None:
            handler = logging.FileHandler(logfile)
        else:
            handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        handlers = [handler]
    for handler in handlers:
        logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger
