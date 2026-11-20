# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=protected-access

"""Bootstrap Device run-rw-command customization."""

from azure.cli.core.aaz import AAZObjectType, AAZStrArg, AAZStrType

from azext_managednetworkfabric.aaz.latest.networkfabric.bootstrapdevice import (
    RunRwCommand as _RunRwCommand,
)


class RunRwCommand(_RunRwCommand):
    """Avoid the Azure CLI internal command argument destination."""

    _args_schema = None

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema._fields.pop("command")
        args_schema._fields_alias_map.pop("--command")
        args_schema.device_command = AAZStrArg(
            options=["--command"],
            arg_group="Body",
            help="Specify the command.",
        )
        return args_schema

    class NetworkBootstrapDevicesRunRwCommand(
        _RunRwCommand.NetworkBootstrapDevicesRunRwCommand
    ):
        """Serialize the remapped command argument."""

        @property
        def content(self):
            content_value, builder = self.new_content_builder(
                self.ctx.args,
                typ=AAZObjectType,
                typ_kwargs={"flags": {"required": True, "client_flatten": True}},
            )
            builder.set_prop("command", AAZStrType, ".device_command")
            builder.set_prop("commandUrl", AAZStrType, ".command_url")
            return self.serialize_content(content_value)
