# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=wildcard-import,unused-wildcard-import,protected-access,duplicate-code
# pylint: disable=anomalous-backslash-in-string
# flake8: noqa


"""
This code inherits the auto-generated code for BMM run data extracts command, and adds retrieval
of custom properties. It also processes the output directory if given and downloads
the results of the command.
"""


from pathlib import Path

from azure.cli.core.aaz import *
from azure.cli.core.azclierror import FileOperationError

from ...aaz.latest.networkcloud.baremetalmachine import \
    RunDataExtract as _RunDataExtract
from ..custom_properties import CustomActionProperties


class RunDataExtract(_RunDataExtract):
    '''Custom class for baremetalmachine run data extract command '''

    _args_schema = None

    # NOTE: There is currently an aaz bug that prevents these operations from being completed
    # in the correct place, post_operations().
    # This is a temporary workaround until the next AAZ release.
    def _output(self, *args, **kwargs):
        return CustomActionProperties._output(self, args, kwargs)

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        if cls._args_schema is not None:
            return cls._args_schema
        cls._args_schema = super()._build_arguments_schema(*args, **kwargs)

        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.output = AAZStrArg(
            options=["--output-directory"],
            arg_group="BareMetalMachineRunDataExtractsParameters",
            help="The output directory where the script execution results will " +
            "be downloaded to from storage blob. Accepts relative or qualified directory path.",
            required=False,
            fmt=AAZStrArgFormat(
                pattern="^(.+)([^\/]*)$"
            )
        )

        return cls._args_schema

    def _execute_operations(self):
        self.pre_operations()
        yield self.BareMetalMachinesRunDataExtract(ctx=self.ctx)()
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
        return super().pre_operations()

    class BareMetalMachinesRunDataExtract(_RunDataExtract.BareMetalMachinesRunDataExtracts):
        '''Custom class for baremetalmachine run data extract command '''

        @classmethod
        def _build_schema_on_200(cls):
            if cls._schema_on_200 is not None:
                return cls._schema_on_200

            cls._schema_on_200 = AAZObjectType()
            CustomActionProperties._build_schema_operation_status_result_read(
                cls._schema_on_200)

            return cls._schema_on_200

        def on_204(self, session):
            pass
