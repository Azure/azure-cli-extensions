# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=unused-wildcard-import,anomalous-backslash-in-string,wildcard-import
# pylint: disable=protected-access,duplicate-code
# flake8: noqa

"""
 This code inherits the auto-generated code for BMM run read command, and adds retrieval of
 custom properties. It also processes the output directory if given and downloads the results
 of the command.
"""

from pathlib import Path

from azure.cli.core.aaz import *
from azure.cli.core.azclierror import FileOperationError

from ...aaz.latest.networkcloud.baremetalmachine import \
    RunReadCommand as _RunReadCommand
from ..custom_properties import CustomActionProperties


class RunReadCommand(_RunReadCommand):
    '''Custom class for baremetalmachine run read command '''

    # Handle custom properties returned by the actions
    # when run read command is executed.
    # The properties object is defined as an interface in the Azure common spec.
    def _output(self, *args, **kwargs):
        return CustomActionProperties._output(self, args, kwargs)

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.output = AAZStrArg(
            options=["--output-directory"],
            arg_group="BareMetalMachineRunReadCommandsParameters",
            help="The output directory where the script execution results will be" +
            " downloaded to from storage blob. Accepts relative or qualified directory path.",
            required=False,
            fmt=AAZStrArgFormat(
                pattern="^(.+)([^\/]*)$"
            )
        )
        return args_schema

    def _execute_operations(self):
        self.pre_operations()
        yield self.BareMetalMachineRunReadCommand(ctx=self.ctx)()
        self.post_operations()

    def pre_operations(self):
        args = self.ctx.args
        output_directory = args.output
        if has_value(args.output):
            try:
                Path(f"{output_directory}").mkdir(
                    parents=True, exist_ok=True)
            except OSError as ex:
                raise FileOperationError(ex) from ex

    class BareMetalMachineRunReadCommand(_RunReadCommand.BareMetalMachinesRunReadCommands):
        '''Custom class for baremetalmachine run read command '''

        @classmethod
        def _build_schema_on_200(cls):
            if cls._schema_on_200 is not None:
                return cls._schema_on_200

            cls._schema_on_200 = AAZObjectType()
            CustomActionProperties._build_schema_operation_status_result_read(
                cls._schema_on_200)

            return cls._schema_on_200

