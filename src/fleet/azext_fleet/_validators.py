# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import semver

from azure.cli.core.azclierror import InvalidArgumentValueError


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
