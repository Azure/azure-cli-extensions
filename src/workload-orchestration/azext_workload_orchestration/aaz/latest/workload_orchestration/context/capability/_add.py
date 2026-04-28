# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: skip-file
# flake8: noqa

"""AAZ command for `workload-orchestration context add-capability`.

Idempotent — at most ONE ARM PATCH call. Skips the call entirely if all
requested capabilities already exist.
"""

from azure.cli.core.aaz import *


@register_command(
    "workload-orchestration context add-capability",
)
class AddCapability(AAZCommand):
    """Add capabilities to a context (idempotent).

    Replaces the painful 7-line PowerShell pattern (show → append → dedup →
    write file → context create) with a single command. Hierarchies and other
    properties are preserved.

    :example: Add a single capability
        az workload-orchestration context add-capability -g Mehoopany --context-name Mehoopany-Context --name soap --description "Soap line"

    :example: Add multiple capabilities (shorthand)
        az workload-orchestration context add-capability -g Mehoopany --context-name Mehoopany-Context --capabilities "[{name:soap,description:Soap},{name:shampoo,description:Shampoo}]"

    :example: Add capabilities from a JSON file
        az workload-orchestration context add-capability -g Mehoopany --context-name Mehoopany-Context --capabilities @new-caps.json
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
            help="Name of a single capability to add (use with --description).",
        )
        _args_schema.description = AAZStrArg(
            options=["--description", "-d"],
            help="Description for the single capability (defaults to name if omitted).",
        )
        _args_schema.capabilities = AAZListArg(
            options=["--capabilities"],
            help=(
                "Capabilities to add. Accepts JSON array, shorthand "
                "(e.g. '[{name:soap,description:Soap}]'), or @file.json. "
                "Each item: {name, description?}."
            ),
        )
        cap_elem = _args_schema.capabilities.Element = AAZObjectArg()
        cap_elem.name = AAZStrArg(help="Capability name.")
        cap_elem.description = AAZStrArg(help="Capability description.")

        return cls._args_schema

    def _handler(self, command_args):
        super()._handler(command_args)

        args = self.ctx.args

        cap_name = args.cap_name.to_serialized_data() if args.cap_name._data is not None else None
        if cap_name == "":
            cap_name = None
        description = args.description.to_serialized_data() if args.description._data is not None else None
        capabilities_raw = args.capabilities.to_serialized_data() if args.capabilities._data is not None else None
        # Treat empty list as not-provided (AAZ may default to [])
        capabilities = capabilities_raw if capabilities_raw else None

        from azext_workload_orchestration.onboarding.context_capability import (
            capability_add as _capability_add,
        )
        return _capability_add(
            cli_ctx=self.cli_ctx,
            resource_group=args.resource_group.to_serialized_data(),
            context_name=args.context_name.to_serialized_data(),
            name=cap_name,
            description=description,
            capabilities=capabilities,
            state=None,
        )


__all__ = ["AddCapability"]
