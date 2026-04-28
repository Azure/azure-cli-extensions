# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: skip-file
# flake8: noqa

"""AAZ command for `workload-orchestration context list-capability`."""

from azure.cli.core.aaz import *


@register_command(
    "workload-orchestration context list-capability",
)
class ListCapability(AAZCommand):
    """List capabilities on a context.

    Returns just the capabilities array (not the full context payload), so
    `-o table` is readable even for contexts with hundreds of capabilities.

    :example: List all capabilities
        az workload-orchestration context list-capability -g Mehoopany --context-name Mehoopany-Context -o table
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
        return cls._args_schema

    def _handler(self, command_args):
        super()._handler(command_args)
        args = self.ctx.args

        from azext_workload_orchestration.onboarding.context_capability import (
            capability_list as _capability_list,
        )
        return _capability_list(
            cli_ctx=self.cli_ctx,
            resource_group=args.resource_group.to_serialized_data(),
            context_name=args.context_name.to_serialized_data(),
            filter_pattern=None,
        )


__all__ = ["ListCapability"]
