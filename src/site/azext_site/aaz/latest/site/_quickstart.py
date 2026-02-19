# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from pathlib import Path
from azure.cli.core.aaz import (  # type: ignore[import-unresolved]
    AAZCommand,
    AAZStrArg,
    AAZStrArgFormat,
    AAZResourceGroupNameArg,
    has_value,
    register_command,
    AAZResourceLocationArg
)
from azure.cli.core.azclierror import (  # type: ignore[import-unresolved]
    InvalidArgumentValueError,
    FileOperationError,
    CLIInternalError,
)
from azure.cli.core import get_default_cli  # type: ignore[import-unresolved]
from knack.log import get_logger

logger = get_logger(__name__)


def _resolve_template_path() -> Path:
    # ...\azext_site\aaz\latest\site\_quickstart.py -> ...\azext_site\templates\infra\main.json
    azext_root = Path(__file__).resolve().parents[3]  # ...\azext_site
    return azext_root / "templates" / "infra" / "main.json"



def _get_deployment_outputs(cli, deployment_name: str, resource_group: str) -> tuple[str | None, str | None]:
    site_id = None
    config_id = None
    try:
        outputs_args = [
            "deployment", "group", "show",
            "--name", deployment_name,
            "--resource-group", resource_group,
            "--only-show-errors",
            "--query", "properties.outputs",
            "--output", "none",
        ]
        cli.invoke(outputs_args)
        if getattr(cli, "result", None) is not None and isinstance(cli.result.result, dict):
            outputs = cli.result.result
            if isinstance(outputs.get("siteId"), dict):
                site_id = outputs.get("siteId", {}).get("value")
            if isinstance(outputs.get("configId"), dict):
                config_id = outputs.get("configId", {}).get("value")
    except Exception:
        return None, None
    return site_id, config_id


def _arm_id_suffix(arm_id: str | None) -> str:
    return f" ARM ID - {arm_id}" if arm_id else ""


def _create_resource_group(cli, rg_name: str, location_arg: str | None) -> str:
    create_loc = (location_arg or "eastus2").strip()
    if not create_loc:
        create_loc = "eastus2"

    create_args = [
        "group", "create",
        "--name", rg_name,
        "--location", create_loc,
        "--only-show-errors",
        "--output", "none",
    ]
    rc = cli.invoke(create_args)
    if rc != 0:
        underlying_error = None
        if getattr(cli, "result", None) is not None:
            underlying_error = getattr(cli.result, "error", None)
        msg = f"Failed to create resource group '{rg_name}' in location '{create_loc}'."
        if underlying_error:
            msg = f"{msg}\nUnderlying error: {underlying_error}"
        raise CLIInternalError(msg)

    return create_loc

@register_command("site quickstart")
class Quickstart(AAZCommand):
    """Quickstart: deploy internal ARM template to create Site + Config + ConfigRef."""

    _args_schema = None

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        if cls._args_schema is not None:
            return cls._args_schema

        cls._args_schema = super()._build_arguments_schema(*args, **kwargs)
        _args_schema = cls._args_schema

        _args_schema.name = AAZStrArg(
            options=["-n", "--name"],
            required=True,
            help="Site name (siteName).",
            fmt=AAZStrArgFormat(
                pattern=r"^[a-zA-Z0-9][a-zA-Z0-9-_.]{0,62}[a-zA-Z0-9]$",
                min_length=2,
                max_length=64,
            ),
        )

        _args_schema.scope = AAZStrArg(
            options=["--scope"],
            help="Scope for site creation. Currently supported: resource-group (default).",
        )

        _args_schema.configuration = AAZStrArg(
            options=["--configuration"],
            help=(
                "Configuration source. Currently supported: defaults. "
                "Use --configuration defaults."
            ),
        )

        _args_schema.resource_group = AAZResourceGroupNameArg(
            options=["-g", "--resource-group"],
            help="Resource group for deployment. If omitted, defaults to '<siteName>-rg' and will be created.",
        )

        _args_schema.location = AAZResourceLocationArg(
            options=["-l", "--location"],
            help="Location. Used only when creating the default resource group (default: eastus2).",
        )

        _args_schema.config_name = AAZStrArg(
            options=["--config-name"],
            help="Optional configName override. Default in template: 'siteName-configuration'.",
        )

        return cls._args_schema

    def _handler(self, command_args):
        super()._handler(command_args)
        return self.handle()

    def handle(self):
        template = _resolve_template_path()
        if not template.exists():
            raise FileOperationError(f"Internal ARM template not found: {template}")

        scope_raw = None
        if has_value(self.ctx.args.scope):
            scope_raw = (self.ctx.args.scope.to_serialized_data() or "").strip()
        scope = (scope_raw or "resource-group").lower()
        if scope != "resource-group":
            raise InvalidArgumentValueError(
                "Invalid --scope value. Currently supported: resource-group."
            )
        
        cfg_raw = None
        if has_value(self.ctx.args.configuration):
            cfg_raw = (self.ctx.args.configuration.to_serialized_data() or "").strip()
        if not cfg_raw:
            cfg_raw = "defaults"
        if cfg_raw.lower() != "defaults":
            raise InvalidArgumentValueError(
                "Invalid --configuration value. Currently supported: defaults."
            )

        site_name = self.ctx.args.name.to_serialized_data()
        cli = get_default_cli()

        location_arg = None
        if has_value(self.ctx.args.location):
            location_arg = self.ctx.args.location.to_serialized_data()

        if has_value(self.ctx.args.resource_group):
            rg = self.ctx.args.resource_group.to_serialized_data()
            rg_location = _create_resource_group(cli, rg, location_arg)
        else:
            rg = f"{site_name}"
            rg_location = _create_resource_group(cli, rg, location_arg)
        
        deployment_name = f"site-quickstart-{site_name}"

        invoke_args = [
            "deployment", "group", "create",
            "--name", deployment_name,
            "--resource-group", rg,
            "--template-file", str(template),
            "--parameters", f"siteName={site_name}",
            "--parameters", f"location={rg_location}",
            "--only-show-errors",
            "--output", "none",
        ]

        if has_value(self.ctx.args.config_name):
            cfg = self.ctx.args.config_name.to_serialized_data()
            invoke_args.extend(["--parameters", f"configName={cfg}"])

        rc = cli.invoke(invoke_args)
        if rc != 0:
            # Capture the original error first (before more invokes overwrite cli.result)
            underlying_error = None
            if getattr(cli, "result", None) is not None:
                underlying_error = getattr(cli.result, "error", None)

            deployment_error = None
            failed_ops = None

            # Try to fetch ARM deployment error object (code/message/details)
            try:
                show_args = [
                    "deployment", "group", "show",
                    "--name", deployment_name,
                    "--resource-group", rg,
                    "--only-show-errors",
                    "--query", "properties.error",
                    "--output", "json",
                ]
                cli.invoke(show_args)
                if getattr(cli, "result", None) is not None:
                    deployment_error = cli.result.result
            except Exception:
                deployment_error = None

            # Try to fetch failed operations (often contains the most actionable message)
            try:
                ops_args = [
                    "deployment", "operation", "group", "list",
                    "--name", deployment_name,
                    "--resource-group", rg,
                    "--only-show-errors",
                    "--query",
                    "[?properties.provisioningState=='Failed']."
                    "{type:properties.targetResource.resourceType,"
                    " name:properties.targetResource.resourceName,"
                    " statusMessage:properties.statusMessage}",
                    "--output", "json",
                ]
                cli.invoke(ops_args)
                if getattr(cli, "result", None) is not None:
                    failed_ops = cli.result.result
            except Exception:
                failed_ops = None

            msg = (
                "ARM deployment failed for site quickstart. "
                f"Deployment name: {deployment_name}, resource group: {rg}."
            )
            if underlying_error:
                msg = f"{msg}\nUnderlying error: {underlying_error}"

            if deployment_error:
                msg = f"{msg}\nDeployment error:\n{json.dumps(deployment_error, indent=2)}"

            if failed_ops:
                msg = f"{msg}\nFailed operations:\n{json.dumps(failed_ops, indent=2)}"

            raise CLIInternalError(msg)

        site_id, config_id = _get_deployment_outputs(cli, deployment_name, rg)
        config_ref_id = (
            f"{site_id}/providers/Microsoft.Edge/configurationReferences/default" if site_id else None
        )

        if site_id or config_id:
            print("Site created successfully." + _arm_id_suffix(site_id))
            print("Config created successfully." + _arm_id_suffix(config_id))
            print("Config reference created successfully." + _arm_id_suffix(config_ref_id))
        else:
            print("Deployment completed successfully.")

        return None