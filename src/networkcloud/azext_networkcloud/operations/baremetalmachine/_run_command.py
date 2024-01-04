# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=protected-access,duplicate-code

"""
This custom code inherits the auto-generated code for BMM run command and adds:
 - retrieval of custom properties returned on the success using CustomActionProperties class.
"""
from azext_networkcloud.aaz.latest.networkcloud.baremetalmachine import (
    RunCommand as _RunCommand,
)
from azext_networkcloud.operations.custom_properties import CustomActionProperties
from azext_networkcloud.operations.run_command_options import RunCommandOptions
from azure.cli.core.aaz import AAZObjectType, AAZStrArg, AAZStrArgFormat


class RunCommand(RunCommandOptions, _RunCommand):
    """Custom class for baremetalmachine run command"""

    # Handle custom properties returned by the actions
    # when run command is executed.
    # The properties object is defined as an interface in the Azure common spec.
    def _output(self, *args, **kwargs):
        return CustomActionProperties._output(self, args, kwargs)

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.output = AAZStrArg(
            options=["--output-directory"],
            arg_group="BareMetalMachineRunCommandParameters",
            help="The output directory where the script execution results will be"
            + "downloaded to from storage blob. Accepts relative or qualified directory path.",
            required=False,
            fmt=AAZStrArgFormat(pattern=r"^(.+)([^\/]*)$"),
        )
        return args_schema

    def _execute_operations(self):
        self.pre_operations()
        yield self.BareMetalMachinesRunCommand(ctx=self.ctx)()
        self.post_operations()

    class BareMetalMachinesRunCommand(_RunCommand.BareMetalMachinesRunCommand):
        """Custom class for baremetal machine run command"""

        @classmethod
        def _build_schema_on_200_201(cls):
            if cls._schema_on_200_201 is not None:
                return cls._schema_on_200_201

            cls._schema_on_200_201 = AAZObjectType()
            CustomActionProperties._build_schema_operation_status_result_read(
                cls._schema_on_200_201
            )

            return cls._schema_on_200_201
