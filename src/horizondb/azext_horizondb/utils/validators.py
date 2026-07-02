# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.prompting import NoTTYException, prompt_pass
from knack.util import CLIError
from azure.cli.core.azclierror import ArgumentUsageError
from azure.cli.core.commands.validators import (
    get_default_location_from_resource_group, validate_tags)
from typing import Any, Dict, Iterable, Optional


def check_resource_group(resource_group_name):
    # check if rg is already null originally
    if not resource_group_name:
        return False

    # replace single and double quotes with empty string
    resource_group_name = resource_group_name.replace("'", '').replace('"', '').strip()

    # check if rg is empty after removing quotes
    if not resource_group_name:
        return False
    return True


def password_validator(ns):
    if not ns.administrator_login_password:
        try:
            ns.administrator_login_password = prompt_pass(msg='Admin Password: ')
        except NoTTYException:
            raise CLIError('Specify --administrator-login-password when running in non-interactive mode.')


def get_combined_validator(validators):
    def _final_validator_impl(cmd, namespace):
        # do additional creation validation
        if cmd.name == 'horizondb create' or cmd.name.endswith(' horizondb create'):
            password_validator(namespace)
            get_default_location_from_resource_group(cmd, namespace)

        validate_tags(namespace)

        for validator in validators:
            validator(namespace)

    return _final_validator_impl


def is_supported_vcore(processor_capabilities: Optional[Dict[str, Any]], vcore_arg: Any) -> bool:
    supported_vcores: Iterable[Any] = (processor_capabilities or {}).get("supportedVcores", [])

    try:
        processor_vcore_options = [int(v) for v in supported_vcores]
        parsed_vcore_arg = int(vcore_arg)
    except (TypeError, ValueError):
        return False

    return parsed_vcore_arg in processor_vcore_options


def validate_resource_group(resource_group_name):
    if not check_resource_group(resource_group_name):
        raise CLIError('Resource group name cannot be empty.')


# Argument Validators
def validate_replica_count(ns):
    if ns.replica_count is None:
        return
    if ns.replica_count < 1 or ns.replica_count > 16:
        raise CLIError('Replica count must be between 1 and 16, inclusive.')


def validate_parameters(cmd, namespace):    # pylint: disable=unused-argument
    if not namespace.parameters:
        return

    from azext_horizondb.vendored_sdks.models import ParameterProperties

    parameter_list = []
    for item in namespace.parameters:
        if '=' not in item:
            raise ArgumentUsageError("Parameter '{}' must be in the format name=value.".format(item))
        name, value = item.split('=', 1)
        parameter_list.append(ParameterProperties(name=name, value=value))

    namespace.parameters = parameter_list
