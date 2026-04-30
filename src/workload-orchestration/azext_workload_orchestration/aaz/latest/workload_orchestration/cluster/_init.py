# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: skip-file
# flake8: noqa

"""AAZ command for `workload-orchestration cluster init`.

Hand-authored AAZ command class that owns argument parsing and delegates the
orchestration to the existing custom target_prepare() function.
"""

from azure.cli.core.aaz import *


@register_command(
    "workload-orchestration cluster init",
)
class Init(AAZCommand):
    """Prepare an Arc-connected Kubernetes cluster for Workload Orchestration.

    Installs all prerequisites on an Arc-connected cluster to make it ready
    for Workload Orchestration. Idempotent - skips components already installed.

    Steps performed:
      1. Verify cluster is Arc-connected with required features enabled
      2. Install Workload Orchestration Extension Dependencies
      3. Install Workload Orchestration Extension
      4. Create Custom Location (validates cluster binding if already exists)

    :example: Initialize a cluster with defaults
        az workload-orchestration cluster init -c my-cluster -g my-rg -l eastus2euap
    :example: Use a specific release train
        az workload-orchestration cluster init -c my-cluster -g my-rg -l eastus2euap --release-train dev
    :example: Pin a specific WO extension version
        az workload-orchestration cluster init -c my-cluster -g my-rg -l eastus2euap --extension-version 2.1.28
    :example: Pin a dependency extension (partial-value shorthand)
        az workload-orchestration cluster init -c my-cluster -g my-rg -l eastus2euap --extension-dependency-version iotplatform=0.7.6
    :example: Pin a dependency extension (full-value shorthand)
        az workload-orchestration cluster init -c my-cluster -g my-rg -l eastus2euap --extension-dependency-version "{iotplatform:0.7.6}"
    :example: Pin dependencies from a JSON file
        az workload-orchestration cluster init -c my-cluster -g my-rg -l eastus2euap --extension-dependency-version deps.json
    :example: Custom location name
        az workload-orchestration cluster init -c my-cluster -g my-rg -l eastus2euap --custom-location-name my-cl
    :example: Custom location in a different resource group
        az workload-orchestration cluster init -c my-cluster -g cluster-rg -l eastus2euap --custom-location-resource-group cl-rg
    :example: Custom location in a different region
        az workload-orchestration cluster init -c my-cluster -g my-rg -l eastus2euap --custom-location-location westus2
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

        _args_schema.cluster_name = AAZStrArg(
            options=["-c", "--cluster-name"],
            required=True,
            help="Name of the Arc-connected Kubernetes cluster.",
        )
        _args_schema.resource_group = AAZResourceGroupNameArg(
            required=True,
            help="Resource group of the Arc-connected cluster.",
        )
        _args_schema.location = AAZResourceLocationArg(
            required=True,
            help="Azure region for the custom location (e.g. eastus2euap).",
        )
        _args_schema.release_train = AAZStrArg(
            options=["--release-train"],
            help="Extension release train. Default: stable.",
        )
        _args_schema.extension_version = AAZStrArg(
            options=["--extension-version"],
            help="Specific WO extension version to install.",
        )
        _args_schema.extension_name = AAZStrArg(
            options=["--extension-name"],
            help="Name for the WO extension resource. Default: wo-extension.",
        )
        _args_schema.custom_location_name = AAZStrArg(
            options=["--custom-location-name"],
            help="Name for the custom location. Default: `{cluster-name}-cl`.",
        )
        _args_schema.custom_location_resource_group = AAZStrArg(
            options=["--custom-location-resource-group"],
            help=(
                "Resource group where the custom location will be created. "
                "Default: same as --resource-group."
            ),
        )
        _args_schema.custom_location_location = AAZStrArg(
            options=["--custom-location-location"],
            help=(
                "Azure region where the custom location will be created. "
                "Default: same as --location."
            ),
        )
        _args_schema.extension_dependency_version = AAZDictArg(
            options=["--extension-dependency-version"],
            help=(
                "Pin dependency extension versions. "
                "Supported key: iotplatform. "
                "Example: iotplatform=0.7.6, {iotplatform:0.7.6}, deps.json."
            ),
        )
        _args_schema.extension_dependency_version.Element = AAZStrArg()

        return cls._args_schema

    def _handler(self, command_args):
        super()._handler(command_args)
        args = self.ctx.args

        from azext_workload_orchestration.common import target_init
        return target_init(
            cmd=self,
            cluster_name=args.cluster_name.to_serialized_data(),
            resource_group=args.resource_group.to_serialized_data(),
            location=args.location.to_serialized_data(),
            release_train=args.release_train.to_serialized_data() if args.release_train._data is not None else None,
            extension_version=args.extension_version.to_serialized_data() if args.extension_version._data is not None else None,
            extension_name=args.extension_name.to_serialized_data() if args.extension_name._data is not None else None,
            custom_location_name=args.custom_location_name.to_serialized_data() if args.custom_location_name._data is not None else None,
            custom_location_resource_group=(
                args.custom_location_resource_group.to_serialized_data()
                if args.custom_location_resource_group._data is not None else None
            ),
            custom_location_location=(
                args.custom_location_location.to_serialized_data()
                if args.custom_location_location._data is not None else None
            ),
            extension_dependency_version=(
                args.extension_dependency_version.to_serialized_data()
                if args.extension_dependency_version._data is not None else None
            ),
        )


__all__ = ["Init"]
