# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,no-member

from abc import ABC
from pathlib import Path

from azure.cli.core.aaz import AAZStrArg, AAZStrArgFormat, has_value
from azure.cli.core.azclierror import FileOperationError


class RunCommandOptions(ABC):
    """Helper class for all BMM commands that allow to download execution result to the disk"""

    def pre_operations(self):
        """
        Adds a command hook to create the output directory for downloading the output result.
        """
        args = self.ctx.args
        output_directory = args.output
        if has_value(args.output):
            try:
                Path(f"{output_directory}").mkdir(parents=True, exist_ok=True)
            except OSError as ex:
                raise FileOperationError(ex) from ex
        return super().pre_operations()

    def _add_output_directory_argument(self, arg_group, *args, **kwargs):
        """
        Adds new argument to collect the output directory for downloading the output result.
        """
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.output = AAZStrArg(
            options=["--output-directory"],
            arg_group=arg_group,
            help="The output directory where the script execution results will be"
            + "downloaded to from storage blob. Accepts relative or qualified directory path.",
            required=False,
            fmt=AAZStrArgFormat(pattern=r"^(.+)([^\/]*)$"),
        )
        return args_schema
