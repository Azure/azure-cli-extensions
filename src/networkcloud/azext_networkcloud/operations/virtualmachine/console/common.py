# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=protected-access, too-few-public-methods

"""
This custom code deregisters the 'console_name' argument of console
and sets the default value to "default".
"""


class VirtualMachineConsole:
    """Common class for VirtualMachineConsole CRUD operations"""

    @classmethod
    def _build_arguments_schema(cls, args_schema):
        # deregister the VM console name argument which users should not interact with
        args_schema.console_name._registered = False
        args_schema.console_name._required = False
        return args_schema

    @classmethod
    def pre_operations(cls, args):
        """ "default" is the default name for the console"""
        args.console_name = "default"
        return args
