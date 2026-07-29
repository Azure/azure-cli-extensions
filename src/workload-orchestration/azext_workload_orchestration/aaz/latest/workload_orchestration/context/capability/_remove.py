# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: skip-file
# flake8: noqa

"""AAZ command for `workload-orchestration context remove-capability`."""

from azure.cli.core.aaz import *


@register_command(
    "workload-orchestration context remove-capability",
    confirmation="Are you sure you want to remove the specified capability(ies) from the context?",
)
class RemoveCapability(AAZCommand):
    """Remove one or more capabilities from a context (idempotent).

    Removing a capability that doesn't exist is a no-op (zero ARM calls).
    The context must retain at least one capability after removal.

    :example: Remove a single capability
        az workload-orchestration context remove-capability -g Mehoopany -n Mehoopany-Context --capabilities "[soap]" --yes

    :example: Remove multiple capabilities
        az workload-orchestration context remove-capability -g Mehoopany -n Mehoopany-Context --capabilities "[soap,shampoo,detergent]" --yes
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
        _args_schema.capabilities = AAZListArg(
            options=["--capabilities"],
            required=True,
            help=(
                "Capability names to remove. String array — accepts shorthand "
                "(e.g. '[soap,shampoo]') or @file.json."
            ),
        )
        _args_schema.capabilities.Element = AAZStrArg()
        _args_schema.force = AAZBoolArg(
            options=["--force"],
            help="Skip in-use validation (placeholder for cross-resource checks).",
            default=False,
        )

        return cls._args_schema

    def _handler(self, command_args):
        super()._handler(command_args)

        args = self.ctx.args
        capabilities_raw = args.capabilities.to_serialized_data() if args.capabilities._data is not None else None
        capabilities = capabilities_raw if capabilities_raw else None
        force = args.force.to_serialized_data() if args.force._data is not None else False

        from azext_workload_orchestration.common.context import (
            capability_remove as _capability_remove,
        )
        return _capability_remove(
            cli_ctx=self.cli_ctx,
            resource_group=args.resource_group.to_serialized_data(),
            context_name=args.context_name.to_serialized_data(),
            name=None,
            names=capabilities,
            force=force,
            yes=True,  # AAZ confirmation= flow already enforced --yes
        )


__all__ = ["RemoveCapability"]
