#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from util import SRC_PATH
import logging
import os
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


check_path = 'vendored_sdks'


def check_init_files():
    """ Check if the vendored_sdks directory contains __init__.py in all extensions """
    ref = []
    # SRC_PATH: azure-cli-extensions\src
    for src_d in os.listdir(SRC_PATH):
        # src_d: azure-cli-extensions\src\ext_name
        src_d_full = os.path.join(SRC_PATH, src_d)
        if os.path.isdir(src_d_full):
            for d in os.listdir(src_d_full):
                if d.startswith('azext_'):
                    # root_dir: azure-cli-extensions\src\ext_name\azext_ext_name
                    ref.append(check_init_recursive(os.path.join(src_d_full, d)))
    return ref


def check_init_recursive(root_dir):
    """ Check if a extension contains __init__.py
    :param root_dir: azure-cli-extensions\src\{ext_name}\azext_{ext_name}
    :param dirpath: azure-cli-extensions\src\{ext_name}\azext_{ext_name}
    :param dirnames: all directories under dirpath, type: List[str]
    :param filenames: all files under dirpath, type: List[str]
    """
    error_flag = False
    for (dirpath, dirnames, filenames) in os.walk(root_dir):
        if dirpath.endswith(check_path):
            # Check __init__.py not exists in the vendored_sdks dir and it contains at least one file
            if '__init__.py' not in filenames and not is_empty_dir(dirpath):
                logger.error(f'Directory {dirpath} does not contain __init__.py, please add it.')
                error_flag = True
    return error_flag


def is_empty_dir(root_dir):
    """ Check if the directory did not contain any file """
    for (dirpath, dirnames, filenames) in os.walk(root_dir):
        if filenames:
            return False
    return True


if __name__ == '__main__':
    ref = check_init_files()
    sys.exit(1) if any(ref) else sys.exit(0)
