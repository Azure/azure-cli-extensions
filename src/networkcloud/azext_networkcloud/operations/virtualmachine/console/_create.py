# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=protected-access, too-few-public-methods


"""
Provides VirtualMachine Console create customization
"""
from azext_networkcloud.aaz.latest.networkcloud.virtualmachine.console._create import (
    Create as _Create,
)
from azure.cli.core.aaz import register_callback

from .common import VirtualMachineConsole


class Create(_Create):
    """This custom code inherits from generate virtual machine functions. It is
    integrated into the generated code via:
    - cli-ext/v20221212preview/ext/src/networkcloud/azext_networkcloud/commands.py
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        return VirtualMachineConsole._build_arguments_schema(args_schema)

    @register_callback
    def pre_operations(self):
        return VirtualMachineConsole.pre_operations(self.ctx.args)
