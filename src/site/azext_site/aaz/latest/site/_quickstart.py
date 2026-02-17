# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from pathlib import Path
from azure.cli.core.aaz import (  # type: ignore[import-unresolved]
    AAZCommand,
    AAZStrArg,
    AAZStrArgFormat,
    AAZBoolArg,
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

        _args_schema.defaultconfiguration = AAZBoolArg(
            options=["--defaultconfiguration", "--default-configuration"],
            help="Trigger the internal ARM template flow (Site + Config + ConfigRef).",
        )

        _args_schema.resource_group = AAZResourceGroupNameArg(
            options=["-g", "--resource-group"],
            required=True,
            help="Resource group for deployment.",
        )

        _args_schema.location = AAZResourceLocationArg(
            options=["-l", "--location"],
            help="Location for the deployment. Default: resource group location.",
        )

        _args_schema.config_name = AAZStrArg(
            options=["--config-name"],
            help="Optional configName override. Default in template: 'siteName-configuration'.",
        )

        return cls._args_schema

    def _handler(self, command_args):
        super()._handler(command_args)

        if not self.ctx.args.defaultconfiguration:
            raise InvalidArgumentValueError("Specify --defaultconfiguration to run quickstart.")

        return self.handle()

    def handle(self):
        template = _resolve_template_path()
        if not template.exists():
            raise FileOperationError(f"Internal ARM template not found: {template}")

        site_name = self.ctx.args.name.to_serialized_data()
        rg = self.ctx.args.resource_group.to_serialized_data()
        deployment_name = f"site-quickstart-{site_name}"

        # 1) Create deployment with fully suppressed output (prevents template/deployment payload from printing)
        invoke_args = [
            "deployment", "group", "create",
            "--name", deployment_name,
            "--resource-group", rg,
            "--template-file", str(template),
            "--parameters", f"siteName={site_name}",
            "--only-show-errors",
            "--output", "none",
        ]

        if has_value(self.ctx.args.location):
            loc = self.ctx.args.location.to_serialized_data()
            invoke_args.extend(["--parameters", f"location={loc}"])

        if has_value(self.ctx.args.config_name):
            cfg = self.ctx.args.config_name.to_serialized_data()
            invoke_args.extend(["--parameters", f"configName={cfg}"])

        cli = get_default_cli()
        rc = cli.invoke(invoke_args)
        if rc != 0:
            underlying_error = None
            if getattr(cli, "result", None) is not None:
                underlying_error = getattr(cli.result, "error", None)
            msg = (
                "ARM deployment failed for site quickstart. "
                f"Deployment name: {deployment_name}, resource group: {rg}."
            )
            if underlying_error:
                msg = f"{msg} Underlying error: {underlying_error}"
            raise CLIInternalError(msg)

        # 2) Query deployment operations and print friendly success messages
        ops_args = [
            "deployment", "operation", "group", "list",
            "--name", deployment_name,
            "--resource-group", rg,
            "--only-show-errors",
            "--output", "none",
        ]
        cli.invoke(ops_args)
        ops = []
        if getattr(cli, "result", None) is not None:
            ops = cli.result.result or []

        succeeded_types = set()
        if isinstance(ops, list):
            for op in ops:
                if not isinstance(op, dict):
                    continue
                props = op.get("properties") or {}
                if not isinstance(props, dict):
                    continue
                if props.get("provisioningState") != "Succeeded":
                    continue
                tr = props.get("targetResource") or {}
                if isinstance(tr, dict):
                    rtype = tr.get("resourceType")
                    if rtype:
                        succeeded_types.add(rtype)
                        
        if "Microsoft.Edge/sites" in succeeded_types:
            print("Site created successfully.")
        if "Microsoft.Edge/Configurations" in succeeded_types:
            print("Config created successfully.")
        if "Microsoft.Edge/configurationReferences" in succeeded_types:
            print("Config reference created successfully.")

        if not ({"Microsoft.Edge/sites", "Microsoft.Edge/Configurations", "Microsoft.Edge/configurationReferences"} & succeeded_types):
            print("Deployment completed successfully.")

        return None