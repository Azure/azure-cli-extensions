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


def _load_template_configuration_children(template_path: Path, config_id: str | None) -> list[dict]:
    """Load child resources under Microsoft.Edge/Configurations from the bundled ARM template.

    Best-effort only: this uses template defaults (no ARM reads).
    """
    try:
        def _resolve_template_value(params: dict, value):
            """Resolve a template value like "[parameters('x')]" to that parameter's defaultValue (best-effort)."""
            if not isinstance(value, str):
                return value

            text = value.strip()
            prefix = "[parameters('"
            suffix = "')]"
            if text.startswith(prefix) and text.endswith(suffix):
                param_name = text[len(prefix):-len(suffix)]
                param_def = params.get(param_name)
                if isinstance(param_def, dict) and "defaultValue" in param_def:
                    return param_def.get("defaultValue")
            return value

        raw = template_path.read_text(encoding="utf-8")
        data = json.loads(raw)
        params = data.get("parameters") if isinstance(data, dict) else None
        params = params if isinstance(params, dict) else {}

        resources = data.get("resources") if isinstance(data, dict) else None
        resources = resources if isinstance(resources, list) else []

        config_resource = None
        for res in resources:
            if not isinstance(res, dict):
                continue
            if (res.get("type") or "").lower() == "microsoft.edge/configurations":
                config_resource = res
                break

        if not isinstance(config_resource, dict):
            return []

        child_resources = config_resource.get("resources")
        child_resources = child_resources if isinstance(child_resources, list) else []

        children: list[dict] = []
        for child in child_resources:
            if not isinstance(child, dict):
                continue

            child_type = child.get("type")
            if not isinstance(child_type, str) or not child_type:
                continue

            child_name = _resolve_template_value(params, child.get("name"))
            if not isinstance(child_name, str) or not child_name:
                continue

            child_kind = _resolve_template_value(params, child.get("kind"))
            if not isinstance(child_kind, str):
                child_kind = None

            child_properties = _resolve_template_value(params, child.get("properties"))
            if not isinstance(child_properties, dict):
                child_properties = {}

            child_id = None
            if config_id:
                child_id = f"{config_id}/{child_type}/{child_name}"

            payload = {
                "id": child_id,
                "type": child_type,
                "name": child_name,
                "properties": child_properties,
            }
            if child_kind:
                payload["kind"] = child_kind

            children.append(payload)

        return children
    except Exception:  # best-effort only
        logger.debug("Failed to load configuration children from template '%s'", template_path)
        return []


def _get_deployment_ops(cli, deployment_name: str, resource_group: str) -> list[dict] | None:
    """Return ARM deployment operations for a group deployment.

    Single call used for both:
    - printing any succeeded resources (site/config/configRef)
    - surfacing failed/canceled operations for error details
    """
    try:
        ops_args = [
            "deployment", "operation", "group", "list",
            "--name", deployment_name,
            "--resource-group", resource_group,
            "--only-show-errors",
            "--query",
            "[].{"
            " state:properties.provisioningState,"
            " type:properties.targetResource.resourceType,"
            " name:properties.targetResource.resourceName,"
            " id:properties.targetResource.id,"
            " statusMessage:properties.statusMessage"
            "}",
            "--output", "none",
        ]
        cli.invoke(ops_args)
        if getattr(cli, "result", None) is not None and isinstance(cli.result.result, list):
            return cli.result.result
    except Exception:
        return None
    return None


def _summarize_deployment_ops(ops: list[dict] | None) -> tuple[str | None, str | None, str | None, list[dict]]:
    """Return (site_id, config_id, config_ref_id, failed_ops) (best-effort)."""
    site_id = None
    config_id = None
    config_ref_id = None
    failed_ops: list[dict] = []

    if not isinstance(ops, list):
        return site_id, config_id, config_ref_id, failed_ops

    for op in ops:
        if not isinstance(op, dict):
            continue

        state = (op.get("state") or "").lower()
        if state == "succeeded":
            r_type_norm = (op.get("type") or "").lower()
            r_id = op.get("id")
            if r_type_norm == "microsoft.edge/sites" and not site_id:
                site_id = r_id
            elif r_type_norm == "microsoft.edge/configurations" and not config_id:
                config_id = r_id
            elif r_type_norm == "microsoft.edge/configurationreferences" and not config_ref_id:
                config_ref_id = r_id
        elif state in ("failed", "canceled"):
            failed_ops.append({
                "type": op.get("type"),
                "name": op.get("name"),
                "state": op.get("state"),
                "statusMessage": op.get("statusMessage"),
            })

    return site_id, config_id, config_ref_id, failed_ops


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

        az_error = CLIInternalError(
            f"Failed to create or update resource group '{rg_name}' in location '{create_loc}'."
        )
        recommendations = [
            "Verify the location is valid, or specify a different one with --location.",
            "Verify you are logged in and have permission to create resource groups in the current subscription.",
        ]
        if underlying_error:
            recommendations.append(f"Review the Azure CLI error details: {underlying_error}")
        az_error.set_recommendation(recommendations)
        raise az_error

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
            help="Resource group for deployment. If omitted, defaults to 'siteName' and will be created.",
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
            az_error = FileOperationError(f"Internal ARM template not found: {template}")
            az_error.set_recommendation([
                "Reinstall or update the 'site' extension to restore the bundled templates.",
                "If you are developing locally, ensure 'templates/infra/main.json' exists under the extension root.",
            ])
            raise az_error

        scope = "resource-group"
        if has_value(self.ctx.args.scope):
            scope = (self.ctx.args.scope.to_serialized_data() or "").strip().lower() or "resource-group"
        if scope != "resource-group":
            az_error = InvalidArgumentValueError("Invalid value for --scope. Only 'resource-group' is supported.")
            az_error.set_recommendation("Use --scope resource-group, or omit --scope to use the default.")
            raise az_error

        configuration = "defaults"
        if has_value(self.ctx.args.configuration):
            configuration = (self.ctx.args.configuration.to_serialized_data() or "").strip() or "defaults"
        if configuration.lower() != "defaults":
            az_error = InvalidArgumentValueError("Invalid value for --configuration. Only 'defaults' is supported.")
            az_error.set_recommendation("Use --configuration defaults, or omit --configuration to use the default.")
            raise az_error

        site_name = self.ctx.args.name.to_serialized_data()
        cli = get_default_cli()

        location_arg = None
        if has_value(self.ctx.args.location):
            location_arg = self.ctx.args.location.to_serialized_data()

        rg = self.ctx.args.resource_group.to_serialized_data() if has_value(self.ctx.args.resource_group) else site_name
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

            all_ops = _get_deployment_ops(cli, deployment_name, rg)
            succeeded_site_id, succeeded_config_id, succeeded_config_ref_id, failed_ops = _summarize_deployment_ops(all_ops)

            # Print succeeded resources even if the overall deployment failed
            if succeeded_site_id:
                print(f"Site created successfully. Azure Resource ID - {succeeded_site_id}")
            if succeeded_config_id:
                print(f"Config created successfully. Azure Resource ID - {succeeded_config_id}")
            if succeeded_config_ref_id:
                print(f"Config reference created successfully. Azure Resource ID - {succeeded_config_ref_id}")

            az_error = CLIInternalError(
                f"Deployment failed to create all required resources. Deployment name '{deployment_name}', resource group '{rg}'."
            )

            recommendations = [
                f"Run: az deployment group show --resource-group {rg} --name {deployment_name} --query properties.error --output jsonc",
                f"Run: az deployment operation group list --resource-group {rg} --name {deployment_name} --output table",
            ]

            if failed_ops:
                failed_summary = "; ".join(
                    f"{op.get('type')} '{op.get('name')}' ({op.get('state')})"
                    for op in failed_ops
                    if isinstance(op, dict)
                )
                if failed_summary:
                    recommendations.append(f"Review failed resources: {failed_summary}")

            if succeeded_site_id or succeeded_config_id or succeeded_config_ref_id:
                recommendations.append("Some resources may have been created. Review the resource group resources and clean up if needed.")

            if underlying_error:
                recommendations.append(f"Review the Azure CLI error details: {underlying_error}")

            az_error.set_recommendation(recommendations)
            raise az_error

        # Success: return structured output (JSON by default).
        all_ops = _get_deployment_ops(cli, deployment_name, rg)
        site_id, config_id, config_ref_id, _ = _summarize_deployment_ops(all_ops)

        child_configs = _load_template_configuration_children(template, config_id)

        return {
            "siteId": site_id,
            "siteName": site_name,
            "type": "Microsoft.Edge/sites",
            "siteConfiguration": {
                "configurationId": config_id,
                "location": rg_location,
                "childConfigurations": child_configs,
                "configurationReferenceId": config_ref_id,
            },
        }
