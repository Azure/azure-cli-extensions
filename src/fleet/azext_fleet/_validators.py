# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re

from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.cli.core.util import CLIError


# https://github.com/Azure/azure-cli/blob/master/doc/authoring_command_modules/authoring_commands.md#supporting-name-or-id-parameters
def validate_member_cluster_id(namespace):
    from msrestazure.tools import is_valid_resource_id
    if not is_valid_resource_id(namespace.member_cluster_id):
        raise InvalidArgumentValueError(
            "--member-cluster-id is not a valid Azure resource ID.")


def validate_kubernetes_version(namespace):
    if namespace.kubernetes_version:
        k8s_release_regex = re.compile(r'^[v|V]?(\d+\.\d+(?:\.\d+)?)$')
        found = k8s_release_regex.findall(namespace.kubernetes_version)
        if not found:
            raise InvalidArgumentValueError(
                '--kubernetes-version should be the full version number '
                'or alias minor version, such as "1.7.12" or "1.7"')


def validate_apiserver_subnet_id(namespace):
    _validate_subnet_id(namespace.apiserver_subnet_id, "--apiserver-subnet-id")


def validate_agent_subnet_id(namespace):
    _validate_subnet_id(namespace.agent_subnet_id, "--agent-subnet-id")


def validate_update_strategy_name(namespace):
    if namespace.update_strategy_name is not None and not namespace.update_strategy_name.strip():
        raise CLIError("--update-strategy-name is not a valid name")


def validate_vm_size(namespace):
    if namespace.vm_size is not None and not namespace.vm_size.strip():
        raise CLIError("--vm-size is not a valid value")


def _validate_subnet_id(subnet_id, name):
    if subnet_id is None or subnet_id == '':
        return
    from msrestazure.tools import is_valid_resource_id
    if not is_valid_resource_id(subnet_id):
        raise CLIError(name + " is not a valid Azure resource ID.")


def validate_assign_identity(namespace):
    if namespace.assign_identity is not None:
        if namespace.assign_identity == '':
            return
        from msrestazure.tools import is_valid_resource_id
        if not is_valid_resource_id(namespace.assign_identity):
            raise CLIError(
                "--assign-identity is not a valid Azure resource ID.")


def validate_targets(namespace):
    ts = namespace.targets
    if not ts:
        raise InvalidArgumentValueError("The target list cannot be None or empty.")

    for t in ts:
        _validate_target(t)


def _validate_target(target):
    if not target:
        raise InvalidArgumentValueError("The target cannot be None or empty.")

    parts = target.split(':')

    # Validate that there is exactly one colon and two non-empty parts
    if len(parts) != 2 or not all(parts):
        raise InvalidArgumentValueError(
            f"The target '{target}' is not in the correct format 'targetType:targetName'. "
            "It must contain exactly one colon and both parts must be non-empty."
            "See help for details."
        )

    valid_keys = {'AfterStageWait', 'Group', 'Member', 'Stage'}
    if parts[0] not in valid_keys:
        raise InvalidArgumentValueError("Invalid target type, valid types are the following case-sensitive values:"
                                        "'AfterStageWait', 'Group', 'Member', or 'Stage'.")
