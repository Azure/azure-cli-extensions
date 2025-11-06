# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import re

from azure.cli.command_modules.resource.custom import (
    _find_missing_parameters,
    _prepare_deployment_properties_unmodified,
)
from azure.cli.core.profiles import ResourceType


class _ResourceDeploymentCommandAdapter:
    """Ensure required resource type defaults are present when reusing resource module helpers."""

    def __init__(self, cmd):
        self._cmd = cmd
        self.cli_ctx = cmd.cli_ctx

    def get_models(self, *attr_args, **kwargs):
        kwargs.setdefault('resource_type', ResourceType.MGMT_RESOURCE_DEPLOYMENTS)
        return self._cmd.get_models(*attr_args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._cmd, name)


def get_parameters(
    arm_template: dict,
    arm_template_parameters: dict,
) -> dict:

    return {
        parameter_key: (
            arm_template_parameters.get(parameter_key, {}).get("value")
            or arm_template.get("parameters", {}).get(parameter_key, {}).get("value")
            or arm_template.get("parameters", {}).get(parameter_key, {}).get("defaultValue")
        )
        for parameter_key in arm_template.get("parameters", {}).keys()
    }


def eval_parameters(
    arm_template: dict,
    arm_template_parameters: dict,
) -> dict:

    parameters = get_parameters(arm_template, arm_template_parameters)
    return json.loads(re.compile(r"\[parameters\(\s*'([^']+)'\s*\)\]").sub(
        lambda match: json.dumps(parameters.get(match.group(1)) or match.group(0))[1:-1],
        json.dumps(arm_template),
    ))


def eval_variables(
    arm_template: dict,
    arm_template_parameters: dict,
) -> dict:

    variables = arm_template.get("variables", {})
    return json.loads(re.compile(r"\[variables\(\s*'([^']+)'\s*\)\]").sub(
        lambda match: json.dumps(variables.get(match.group(1), match.group(0)))[1:-1],
        json.dumps(arm_template),
    ))


EVAL_FUNCS = [
    eval_parameters,
    eval_variables,
]

def parse_deployment_template(
    az_cli_command,
    template: str,
    parameters: dict,
) -> dict:
    properties = _prepare_deployment_properties_unmodified(
        cmd=_ResourceDeploymentCommandAdapter(az_cli_command),
        deployment_scope='resourceGroup',
        template_file=template,
        parameters=parameters,
        no_prompt=True,
    )
    template = json.loads(properties.template)
    parameters = properties.parameters or {}

    for eval_func in EVAL_FUNCS:
        template = eval_func(template, parameters)

    return template

