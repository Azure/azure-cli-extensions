# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,no-member

from abc import ABC
from pathlib import Path

from azure.cli.core.aaz import has_value
from azure.cli.core.azclierror import FileOperationError


class RunCommandOptions(ABC):
    """
    This class adds a command hook to create a directory in the output directory
    the user provides with the output argument.
    """

    def pre_operations(self):
        args = self.ctx.args
        output_directory = args.output
        if has_value(args.output):
            try:
                Path(f"{output_directory}").mkdir(parents=True, exist_ok=True)
            except OSError as ex:
                raise FileOperationError(ex) from ex
        return super().pre_operations()
