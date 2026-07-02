# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.prompting import NoTTYException, prompt_pass
from knack.util import CLIError
from azure.cli.core.commands.validators import (
    get_default_location_from_resource_group, validate_tags)
from azure.cli.core.util import parse_proxy_resource_id
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


def validate_private_endpoint_connection_id(cmd, namespace):  # pylint: disable=unused-argument
    if getattr(namespace, 'connection_id', None):
        result = parse_proxy_resource_id(namespace.connection_id)
        provider_type = '{}/{}'.format(result.get('namespace'), result.get('type')).lower() if result else ''
        child_type = (result.get('child_type_1') or '').lower() if result else ''
        if (not result or
                provider_type != 'microsoft.horizondb/clusters' or
                child_type != 'privateendpointconnections' or
                result.get('last_child_num') != 1):
            raise CLIError('The --id value must be a HorizonDB cluster private endpoint connection resource ID.')
        namespace.resource_group_name = result.get('resource_group')
        namespace.cluster_name = result.get('name')
        namespace.private_endpoint_connection_name = result.get('child_name_1')

    if not all([
            getattr(namespace, 'resource_group_name', None),
            getattr(namespace, 'cluster_name', None),
            getattr(namespace, 'private_endpoint_connection_name', None)]):
        raise CLIError(
            'Specify either --id <private-endpoint-connection-id> or '
            '--name <private-endpoint-connection-name> --cluster-name <cluster-name> '
            '--resource-group <resource-group>.')

    if hasattr(namespace, 'connection_id'):
        del namespace.connection_id
