# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,no-member

from abc import ABC
from pathlib import Path

from azure.cli.core.aaz import AAZStrArg, AAZStrArgFormat, has_value
from azure.cli.core.azclierror import FileOperationError, RequiredArgumentMissingError


class RunCommandOptions(ABC):
    """Helper class for all BMM commands that allow to download execution result to the disk"""

    def pre_operations(self):
        """
        Adds a command hook to create the output directory for downloading the output result.
        """
        args = self.ctx.args
        output_directory = args.output
        if has_value(args.output):
            if not has_value(args.expected_storage_host):
                raise RequiredArgumentMissingError(
                    "--output-directory requires --expected-storage-host"
                )
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
        args_schema.expected_storage_host = AAZStrArg(
            options=["--expected-storage-host"],
            arg_group=arg_group,
            help="Exact trusted storage hostname. Required with --output-directory.",
        )
        args_schema.expected_sha256 = AAZStrArg(
            options=["--expected-sha256"],
            arg_group=arg_group,
            help="Optional trusted SHA-256 digest of the compressed result archive. "
            "Verified before extraction when provided.",
            fmt=AAZStrArgFormat(pattern=r"^[A-Fa-f0-9]{64}$"),
        )
        return args_schema
