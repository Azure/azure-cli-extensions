# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from pathlib import Path
from azure.cli.core.aaz import (  # type: ignore[import-unresolved]
    AAZCommand,
    AAZStrArg,
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
        )

        _args_schema.defaultconfiguration = AAZBoolArg(
            options=["--defaultconfiguration", "--default-configuration"],
            help="Trigger the internal ARM template flow (Site + Config + ConfigRef).",
        )

        _args_schema.resource_group = AAZResourceGroupNameArg(
            options=["-g", "--resource-group"],
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

        invoke_args = [
            "deployment", "group", "create",
            "--name", deployment_name,
            "--resource-group", rg,
            "--template-file", str(template),
            "--parameters",
            f"siteName={site_name}",
        ]

        if has_value(self.ctx.args.location):
            loc = self.ctx.args.location.to_serialized_data()
            invoke_args.extend(["--parameters", f"location={loc}"])

        if has_value(self.ctx.args.config_name):
            cfg = self.ctx.args.config_name.to_serialized_data()
            invoke_args.append(f"configName={cfg}")

        cli = get_default_cli()
        rc = cli.invoke(invoke_args)
        if rc != 0:
            # Include deployment context and underlying CLI error (if any) for easier troubleshooting.
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

        return cli.result.result
