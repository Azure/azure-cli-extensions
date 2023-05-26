# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=unused-wildcard-import,anomalous-backslash-in-string,wildcard-import
# pylint: disable=protected-access,duplicate-code
# flake8: noqa

"""
This custom code inherits the auto-generated code for BMM run command and adds:
 - retrieval of custom properties returned on the success using CustomActionProperties class.
"""

from pathlib import Path

from azure.cli.core.aaz import *
from azure.cli.core.azclierror import FileOperationError

from ...latest.networkcloud.baremetalmachine import RunCommand as _RunCommand
from ..custom_properties import CustomActionProperties


class RunCommand(_RunCommand):
    '''Custom class for baremetalmachine run command '''
    _args_schema = None

    # NOTE: There is currently an aaz bug that prevents these operations from being completed
    # in the correct place, post_operations(). This is a temporary workaround until
    # the next AAZ release.
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
            arg_group="BareMetalMachineRunCommandParameters",
            help="The output directory where the script execution results will be" +
            "downloaded to from storage blob. Accepts relative or qualified directory path.",
            required=False,
            fmt=AAZStrArgFormat(
                pattern="^(.+)([^\/]*)$"
            )
        )

        return cls._args_schema

    def _execute_operations(self):
        self.pre_operations()
        yield self.BareMetalMachinesRunCommand(ctx=self.ctx)()
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

    class BareMetalMachinesRunCommand(_RunCommand.BareMetalMachinesRunCommand):
        ''' Custom class for baremetal machine run command'''
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
