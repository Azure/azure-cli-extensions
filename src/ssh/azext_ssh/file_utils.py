# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import errno
import os
from azure.cli.core import azclierror
from knack import log

logger = log.get_logger(__name__)


def make_dirs_for_file(file_path):
    if not os.path.exists(file_path):
        mkdir_p(os.path.dirname(file_path))


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python <= 2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def delete_file(file_path, message, warning=False):
    # pylint: disable=broad-except
    if os.path.isfile(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            if warning:
                logger.warning(message)
            else:
                raise azclierror.FileOperationError(message + "Error: " + str(e)) from e


def delete_folder(dir_path, message, warning=False):
    # pylint: disable=broad-except
    if os.path.isdir(dir_path):
        try:
            os.rmdir(dir_path)
        except Exception as e:
            if warning:
                logger.warning(message)
            else:
                raise azclierror.FileOperationError(message + "Error: " + str(e)) from e


def create_directory(file_path, error_message):
    try:
        os.makedirs(file_path)
    except Exception as e:
        raise azclierror.FileOperationError(error_message + "Error: " + str(e)) from e


def write_to_file(file_path, mode, content, error_message, encoding=None):
    try:
        if encoding:
            with open(file_path, mode, encoding=encoding) as f:
                f.write(content)
        else:
            with open(file_path, mode) as f:
                f.write(content)
    except Exception as e:
        raise azclierror.FileOperationError(error_message + "Error: " + str(e)) from e
