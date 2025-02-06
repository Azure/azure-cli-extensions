# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.core import azclierror, telemetry
from knack import log

import azext_connectedk8s._constants as consts

logger = log.get_logger(__name__)


def delete_file(file_path: str, message: str, warning: bool = False) -> None:
    # pylint: disable=broad-except
    if os.path.isfile(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            telemetry.set_exception(
                exception=e,
                fault_type=consts.Remove_File_Fault_Type,
                summary=f"Unable to delete file at {file_path}",
            )
            if warning:
                logger.warning(message)
            else:
                raise azclierror.FileOperationError(message + "Error: " + str(e)) from e


def create_directory(file_path: str, error_message: str) -> None:
    try:
        os.makedirs(file_path)
    except Exception as e:
        telemetry.set_exception(
            exception=e,
            fault_type=consts.Create_Directory_Fault_Type,
            summary="Unable to create installation directory",
        )
        raise azclierror.FileOperationError(error_message + "Error: " + str(e)) from e
