# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.prompting import NoTTYException, prompt_pass
from knack.util import CLIError
from azure.cli.core.commands.validators import (
    get_default_location_from_resource_group, validate_tags)
from typing import Any, Dict, Iterable, Optional


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
