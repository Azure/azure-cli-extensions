# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.azclierror import InvalidArgumentValueError


# https://github.com/Azure/azure-cli/blob/master/doc/authoring_command_modules/authoring_commands.md#supporting-name-or-id-parameters
def validate_member_cluster_id(namespace):
    from msrestazure.tools import is_valid_resource_id
    if not is_valid_resource_id(namespace.member_cluster_id):
        raise InvalidArgumentValueError(
            "--member-cluster-id is not a valid Azure resource ID.")
