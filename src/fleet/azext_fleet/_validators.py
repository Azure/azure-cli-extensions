# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import semver

from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.cli.core.util import CLIError


# https://github.com/Azure/azure-cli/blob/master/doc/authoring_command_modules/authoring_commands.md#supporting-name-or-id-parameters
def validate_member_cluster_id(namespace):
    from msrestazure.tools import is_valid_resource_id
    if not is_valid_resource_id(namespace.member_cluster_id):
        raise InvalidArgumentValueError(
            "--member-cluster-id is not a valid Azure resource ID.")


def validate_upgrade_type(namespace):
    upgrade_type = namespace.upgrade_type
    if upgrade_type not in ("Full", "NodeImageOnly"):
        raise InvalidArgumentValueError(
            "--upgrade-type must be set to 'Full' or 'NodeImageOnly'")


def validate_kubernetes_version(namespace):
    try:
        if namespace.kubernetes_version:
            semver.VersionInfo.parse(namespace.kubernetes_version)
    except ValueError:
        raise InvalidArgumentValueError(
            "--kubernetes-version must be set as version x.x.x (eg. 1.2.3)")


def validate_apiserver_subnet_id(namespace):
    _validate_subnet_id(namespace.apiserver_subnet_id, "--apiserver-subnet-id")


def validate_agent_subnet_id(namespace):
    _validate_subnet_id(namespace.agent_subnet_id, "--agent-subnet-id")


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
