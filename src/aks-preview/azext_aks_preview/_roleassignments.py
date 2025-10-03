# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.command_modules.acs._roleassignments import add_role_assignment


def add_role_assignment(
    cmd,
    role,
    service_principal_msi_id,
    is_service_principal=True,
    delay=2,
    scope=None,
    assignee_principal_type=None,
):
    return add_role_assignment(
        cmd,
        role,
        service_principal_msi_id,
        is_service_principal,
        delay,
        scope,
        assignee_principal_type,
    )
