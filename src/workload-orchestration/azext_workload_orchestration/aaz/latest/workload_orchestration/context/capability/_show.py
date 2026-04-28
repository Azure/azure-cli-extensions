# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: skip-file
# flake8: noqa

"""AAZ command for `workload-orchestration context show-capability`."""

from azure.cli.core.aaz import *


@register_command(
    "workload-orchestration context show-capability",
)
class ShowCapability(AAZCommand):
    """Show a single capability on a context (case-insensitive name match).

    :example: Show a capability
        az workload-orchestration context show-capability -g Mehoopany --context-name Mehoopany-Context --cap-name soap
    """

    _aaz_info = {
        "version": "1.0.0",
        "resources": [],
    }

    _args_schema = None

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        if cls._args_schema is not None:
            return cls._args_schema
        cls._args_schema = super()._build_arguments_schema(*args, **kwargs)
        _args_schema = cls._args_schema

        _args_schema.resource_group = AAZResourceGroupNameArg(
            required=True,
            help="Resource group of the context.",
        )
        _args_schema.context_name = AAZStrArg(
            options=["-n", "--name", "--context-name"],
            required=True,
            help="Name of the context.",
        )
        _args_schema.cap_name = AAZStrArg(
            options=["--cap-name", "--capability-name"],
            required=True,
            help="Capability name to look up.",
        )
        return cls._args_schema

    def _handler(self, command_args):
        super()._handler(command_args)
        args = self.ctx.args

        from azext_workload_orchestration.onboarding.context_capability import (
            capability_show as _capability_show,
        )
        return _capability_show(
            cli_ctx=self.cli_ctx,
            resource_group=args.resource_group.to_serialized_data(),
            context_name=args.context_name.to_serialized_data(),
            name=args.cap_name.to_serialized_data(),
        )


__all__ = ["ShowCapability"]
