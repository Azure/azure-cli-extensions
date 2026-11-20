# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------

"""Shared run-validation command configuration customization."""

# pylint: disable=no-member,too-few-public-methods

from azure.cli.core.aaz import (
    AAZFreeFormDictArg,
    AAZFreeFormDictType,
    AAZListArg,
    AAZListType,
    AAZObjectArg,
    AAZObjectType,
    AAZStrArg,
    AAZStrType,
)


class RunValidationCommandConfig:
    """Add the command fields omitted from the generated base model."""

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        command_config = args_schema.command_config
        command_config.commands_url = AAZStrArg(
            options=["commands-url"],
            help="URL to a file containing device commands.",
        )
        command_config.commands = AAZListArg(
            options=["commands"],
            help="List of device commands to execute as part of validation.",
        )
        command_config.commands.Element = AAZObjectArg()
        command = command_config.commands.Element
        command.check_name = AAZStrArg(
            options=["check-name"],
            help="Unique check name that identifies this command.",
            required=True,
        )
        command.command = AAZStrArg(
            options=["command"],
            help="The CLI command to execute on the device.",
            required=True,
        )
        command.description = AAZStrArg(
            options=["description"],
            help="Description of what this command validates.",
        )
        command.validation_rules = AAZFreeFormDictArg(
            options=["validation-rules"],
            help="Optional validation rules to apply to the command output.",
        )
        return args_schema


class RunValidationContent:
    """Serialize file-based and inline command configuration fields."""

    @property
    def content(self):
        content = super().content
        config_value, builder = self.new_content_builder(
            self.ctx.args,
            typ=AAZObjectType,
        )
        builder.set_prop("commandsUrl", AAZStrType, ".command_config.commands_url")
        builder.set_prop("commands", AAZListType, ".command_config.commands")

        commands = builder.get(".commands")
        if commands is not None:
            commands.set_elements(AAZObjectType, ".")

        command = builder.get(".commands[]")
        if command is not None:
            command.set_prop(
                "checkName",
                AAZStrType,
                ".check_name",
                typ_kwargs={"flags": {"required": True}},
            )
            command.set_prop(
                "command",
                AAZStrType,
                ".command",
                typ_kwargs={"flags": {"required": True}},
            )
            command.set_prop("description", AAZStrType, ".description")
            command.set_prop(
                "validationRules", AAZFreeFormDictType, ".validation_rules"
            )

        command_config = self.serialize_content(config_value)
        if command_config:
            content["deviceCommandConfiguration"].update(command_config)
        return content
