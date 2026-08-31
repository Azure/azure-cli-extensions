# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: skip-file
# flake8: noqa

"""AAZ command for `workload-orchestration init`.

Hand-authored AAZ command that prepares an Arc-connected Kubernetes cluster for
Workload Orchestration (identical to `workload-orchestration cluster init`) and,
as an additional step, creates a Context resource.
"""

import json
import logging

from azure.cli.core.aaz import *

logger = logging.getLogger(__name__)


@register_command(
    "workload-orchestration init",
)
class Init(AAZCommand):
    """Prepare an Arc-connected cluster for Workload Orchestration and create a Context.

    Steps performed:
      1. Verify cluster is Arc-connected with required features enabled
      2. Install Workload Orchestration Extension Dependencies
      3. Install Workload Orchestration Extension
      4. Create Custom Location (validates cluster binding if already exists)
      5. Create Context resource

    :example: Initialize a cluster and create a context
        az workload-orchestration init -c my-cluster -g my-rg -l eastus2euap --context-name MyContext --context-location eastus --capabilities '[{"description":"desc","name":"cap1"}]' --hierarchies '[{"description":"desc","name":"country"}]'
    :example: Use a specific release train
        az workload-orchestration init -c my-cluster -g my-rg -l eastus2euap --release-train dev --context-name MyContext --context-location eastus --capabilities '[{"description":"desc","name":"cap1"}]' --hierarchies '[{"description":"desc","name":"country"}]'
    :example: Create the context in a different resource group / region
        az workload-orchestration init -c my-cluster -g my-rg -l eastus2euap --context-name MyContext --context-resource-group ctx-rg --context-location eastus --capabilities '[{"description":"desc","name":"cap1"}]' --hierarchies '[{"description":"desc","name":"country"}]'
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

        # ------------------------------------------------------------------
        # Cluster init arguments (identical to `cluster init`)
        # ------------------------------------------------------------------
        _args_schema.cluster_name = AAZStrArg(
            options=["-c", "--cluster-name"],
            arg_group="Cluster",
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
            arg_group="Cluster",
            help="Extension release train. Default: stable.",
        )
        _args_schema.extension_version = AAZStrArg(
            options=["--extension-version"],
            arg_group="Cluster",
            help="Specific WO extension version to install.",
        )
        _args_schema.extension_name = AAZStrArg(
            options=["--extension-name"],
            arg_group="Cluster",
            help="Name for the WO extension resource. Default: wo-extension.",
        )
        _args_schema.custom_location_name = AAZStrArg(
            options=["--custom-location-name"],
            arg_group="Cluster",
            help="Name for the custom location. Default: `{cluster-name}-cl`.",
        )
        _args_schema.custom_location_resource_group = AAZStrArg(
            options=["--custom-location-resource-group"],
            arg_group="Cluster",
            help=(
                "Resource group where the custom location will be created. "
                "Default: same as --resource-group."
            ),
        )
        _args_schema.custom_location_location = AAZStrArg(
            options=["--custom-location-location"],
            arg_group="Cluster",
            help=(
                "Azure region where the custom location will be created. "
                "Default: same as --location."
            ),
        )
        _args_schema.extension_dependency_version = AAZDictArg(
            options=["--extension-dependency-version"],
            arg_group="Cluster",
            help=(
                "Pin dependency extension versions. "
                "Supported key: iotplatform. "
                "Example: iotplatform=0.7.6, {iotplatform:0.7.6}, deps.json."
            ),
        )
        _args_schema.extension_dependency_version.Element = AAZStrArg()

        # ------------------------------------------------------------------
        # Context create arguments
        # ------------------------------------------------------------------
        _args_schema.context_name = AAZStrArg(
            options=["--context-name"],
            arg_group="Context",
            required=True,
            help="The name of the Context to create.",
            fmt=AAZStrArgFormat(
                pattern="^[a-zA-Z0-9]([-a-zA-Z0-9]*[a-zA-Z0-9])?(\\.[a-zA-Z0-9]([-a-zA-Z0-9]*[a-zA-Z0-9])?)*$",
                max_length=61,
                min_length=3,
            ),
        )
        _args_schema.context_resource_group = AAZStrArg(
            options=["--context-resource-group"],
            arg_group="Context",
            help=(
                "Resource group where the Context will be created. "
                "Default: same as --resource-group."
            ),
        )
        _args_schema.context_location = AAZStrArg(
            options=["--context-location"],
            arg_group="Context",
            required=True,
            help="Azure region where the Context will be created.",
        )
        _args_schema.capabilities = AAZListArg(
            options=["--capabilities"],
            arg_group="Context",
            required=True,
            help="List of Capabilities.",
        )
        _args_schema.capabilities.Element = AAZObjectArg()
        _capability = _args_schema.capabilities.Element
        _capability.description = AAZStrArg(
            options=["description"],
            required=True,
            help="Description of Capability.",
        )
        _capability.name = AAZStrArg(
            options=["name"],
            required=True,
            help="Name of Capability.",
        )
        _capability.state = AAZStrArg(
            options=["state"],
            help="State of resource.",
            enum={"active": "active", "inactive": "inactive"},
        )
        _args_schema.hierarchies = AAZListArg(
            options=["--hierarchies"],
            arg_group="Context",
            required=True,
            help="List of Hierarchies.",
        )
        _args_schema.hierarchies.Element = AAZObjectArg()
        _hierarchy = _args_schema.hierarchies.Element
        _hierarchy.description = AAZStrArg(
            options=["description"],
            required=True,
            help="Description of Hierarchy.",
        )
        _hierarchy.name = AAZStrArg(
            options=["name"],
            required=True,
            help="Name of Hierarchy.",
        )
        _args_schema.tags = AAZDictArg(
            options=["--tags"],
            arg_group="Context",
            help="Context resource tags.",
        )
        _args_schema.tags.Element = AAZStrArg()
        _args_schema.site_id = AAZStrArg(
            options=["--site-id"],
            arg_group="Context",
            help="ARM resource ID of a Site to auto-create a site reference after context creation.",
        )

        return cls._args_schema

    def _handler(self, command_args):
        super()._handler(command_args)
        args = self.ctx.args

        # Step 1-4: prepare the cluster (same as `cluster init`).
        from azext_workload_orchestration.common import target_init
        cluster_result = target_init(
            cmd=self,
            cluster_name=args.cluster_name.to_serialized_data(),
            resource_group=args.resource_group.to_serialized_data(),
            location=args.location.to_serialized_data(),
            release_train=args.release_train.to_serialized_data() if has_value(args.release_train) else None,
            extension_version=args.extension_version.to_serialized_data() if has_value(args.extension_version) else None,
            extension_name=args.extension_name.to_serialized_data() if has_value(args.extension_name) else None,
            custom_location_name=args.custom_location_name.to_serialized_data() if has_value(args.custom_location_name) else None,
            custom_location_resource_group=(
                args.custom_location_resource_group.to_serialized_data()
                if has_value(args.custom_location_resource_group) else None
            ),
            custom_location_location=(
                args.custom_location_location.to_serialized_data()
                if has_value(args.custom_location_location) else None
            ),
            extension_dependency_version=(
                args.extension_dependency_version.to_serialized_data()
                if has_value(args.extension_dependency_version) else None
            ),
        )

        # Step 5: create the Context resource.
        context_result = self._create_context(args)

        output = {
            "cluster": cluster_result,
        }
        # Only include the context when it was created; on the already-exists
        # path context_result is None and the key is omitted.
        if context_result is not None:
            output["context"] = context_result
        return output

    @staticmethod
    def _exception_chain_text(exc):
        """Collect message text from an exception and everything it wraps.

        The child ``context create`` invocation can surface its failure in
        different shapes depending on the CLI/test harness: a plain
        ``CLIInternalError`` at runtime, or a wrapper such as testsdk's
        ``CliExecutionError`` (which stores the original error on an
        ``exception`` attribute) whose own ``str()`` is generic. Walk the
        ``exception``/``__cause__``/``__context__`` chain so callers can
        reliably inspect the underlying service error message (e.g.
        ``ContextAlreadyExists``) regardless of the wrapping.
        """
        parts = []
        seen = set()
        current = exc
        while current is not None and id(current) not in seen:
            seen.add(id(current))
            parts.append(str(current))
            wrapped = getattr(current, "exception", None)
            if wrapped is not None and id(wrapped) not in seen:
                seen.add(id(wrapped))
                parts.append(str(wrapped))
            current = getattr(current, "__cause__", None) or getattr(current, "__context__", None)
        return " ".join(p for p in parts if p)

    def _create_context(self, args):
        """Create a Context resource by invoking `context create` in-process.
        """
        from azext_workload_orchestration.common.utils import (
            invoke_cli_command, _eprint,
        )

        context_name = args.context_name.to_serialized_data()
        context_rg = (
            args.context_resource_group.to_serialized_data()
            if has_value(args.context_resource_group)
            else args.resource_group.to_serialized_data()
        )
        context_location = args.context_location.to_serialized_data()
        capabilities = args.capabilities.to_serialized_data()
        hierarchies = args.hierarchies.to_serialized_data()

        cli_args = [
            "workload-orchestration", "context", "create",
            "-g", context_rg,
            "--name", context_name,
            "--location", context_location,
            "--capabilities", json.dumps(capabilities),
            "--hierarchies", json.dumps(hierarchies),
        ]

        if has_value(args.tags):
            tags = args.tags.to_serialized_data()
            tag_args = [f"{key}={value}" for key, value in tags.items()]
            if tag_args:
                cli_args += ["--tags"] + tag_args

        if has_value(args.site_id):
            cli_args += ["--site-id", args.site_id.to_serialized_data()]

        _eprint(f"\nCreating Context: '{context_name}'...")
        # Suppress the child command's ERROR-level logging while it runs — we
        # decide how to surface any failure ourselves (warning vs error) once
        # logging is restored in the finally block.
        logging.disable(logging.ERROR)
        caught = None
        result = None
        try:
            result = invoke_cli_command(self, cli_args)
        except Exception as exc:
            # 'context create' may fail with the tenant's single-Context
            # "already exists" error. Depending on the CLI/test harness this is
            # raised as a CLIInternalError (normal runtime) or wrapped in
            # another type (e.g. testsdk's CliExecutionError). Catch broadly and
            # decide below whether it is the benign already-exists case.
            caught = exc
        finally:
            logging.disable(logging.NOTSET)

        # Failure path.
        if caught is not None:
            message = self._exception_chain_text(caught)
            if "contextalreadyexists" in message.lower():
                # Already exists → surface as a warning (non-fatal).
                yellow, reset = "\033[33m", "\033[0m"
                _eprint(f"{yellow}{message}{reset}\n")
                return None
            # Any other failure → surface as an error.
            raise caught

        # Happy path: Context created → set it as the current context.
        _eprint(f"  ├── Context: '{context_name}' Created ✓")
        self._set_current_context(result)
        return result

    def _set_current_context(self, result):
        """Set the created Context as the current context in CLI config.

        """
        from azext_workload_orchestration.common.utils import (
            set_current_context_config, _eprint,
        )

        context_id = result.get("id") if isinstance(result, dict) else None
        if not context_id:
            return

        set_current_context_config(self.ctx.cli_ctx, context_id)
        _eprint(f"  └── Context set to current ✓\n")


__all__ = ["Init"]