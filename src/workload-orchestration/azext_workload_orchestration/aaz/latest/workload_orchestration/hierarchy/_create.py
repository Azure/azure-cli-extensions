# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: skip-file
# flake8: noqa

"""AAZ command for `workload-orchestration hierarchy create`.

Hand-authored AAZ command class that owns argument parsing (giving us native
shorthand / @file / JSON / YAML support from AAZShortHandSyntaxParser for
free) and delegates the orchestration to the existing custom function.
"""

from azure.cli.core.aaz import *


@register_command(
    "workload-orchestration hierarchy create",
)
class Create(AAZCommand):
    """Create a hierarchy: Site + Configuration + ConfigurationReference (and ServiceGroup ancestors if type=ServiceGroup).

    Idempotent. Supports ResourceGroup (default, single site) and ServiceGroup
    (nested, up to 3 levels) hierarchy types.

    :example: Create RG hierarchy from YAML file
        az workload-orchestration hierarchy create -g my-rg -l eastus2euap --hierarchy-spec hierarchy.yaml
    :example: Create RG hierarchy with inline shorthand
        az workload-orchestration hierarchy create -g my-rg -l eastus2euap --hierarchy-spec "{name:Mehoopany,level:factory}"
    :example: Create ServiceGroup hierarchy from JSON file
        az workload-orchestration hierarchy create -g my-rg -l eastus2euap --hierarchy-spec sg-hierarchy.json
    :example: Create ServiceGroup hierarchy with inline shorthand (children as array)
        az workload-orchestration hierarchy create -g my-rg -l eastus2euap --hierarchy-spec "{type:ServiceGroup,name:India,level:country,children:[{name:Karnataka,level:region,children:[{name:BangaloreSouth,level:factory}]}]}"
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
            help="Resource group for Configuration resources.",
        )
        _args_schema.configuration_location = AAZStrArg(
            options=["-l", "--configuration-location"],
            required=True,
            help="Azure region for the Configuration resource (e.g. eastus2euap).",
        )
        _args_schema.hierarchy_spec = AAZObjectArg(
            options=["--hierarchy-spec"],
            required=True,
            help=(
                "Hierarchy spec. Required keys: name, level. "
                "Optional: type (ResourceGroup|ServiceGroup, default "
                "ResourceGroup), children (list of child specs, ServiceGroup "
                "only, up to 3 levels deep)."
            ),
            blank={},
        )
        _args_schema.hierarchy_spec.name = AAZStrArg(
            help="Hierarchy node name (alphanumeric + hyphen, 2-63 chars).",
        )
        _args_schema.hierarchy_spec.level = AAZStrArg(
            help="Hierarchy level label (e.g. factory, region, country).",
        )
        _args_schema.hierarchy_spec.type = AAZStrArg(
            enum={"ResourceGroup": "ResourceGroup", "ServiceGroup": "ServiceGroup"},
            help="Hierarchy type. Default: ResourceGroup.",
        )
        _args_schema.hierarchy_spec.children = AAZListArg(
            help="Child specs (ServiceGroup only). Must be a list/array.",
        )
        # First-level children element (recursive depth limited to 3 total by
        # the orchestrator; we define two nested layers explicitly here to
        # keep the AAZ schema concrete).
        l1 = _args_schema.hierarchy_spec.children.Element = AAZObjectArg()
        l1.name = AAZStrArg()
        l1.level = AAZStrArg()
        l1.children = AAZListArg()
        l2 = l1.children.Element = AAZObjectArg()
        l2.name = AAZStrArg()
        l2.level = AAZStrArg()
        l2.children = AAZListArg()
        l3 = l2.children.Element = AAZObjectArg()
        l3.name = AAZStrArg()
        l3.level = AAZStrArg()

        return cls._args_schema

    def _handler(self, command_args):
        super()._handler(command_args)

        args = self.ctx.args
        spec = args.hierarchy_spec.to_serialized_data()

        from azext_workload_orchestration.common.hierarchy import (
            hierarchy_create as _hierarchy_create,
        )
        return _hierarchy_create(
            cmd=self,
            resource_group=args.resource_group.to_serialized_data(),
            configuration_location=args.configuration_location.to_serialized_data(),
            hierarchy_spec=spec,
        )


__all__ = ["Create"]
