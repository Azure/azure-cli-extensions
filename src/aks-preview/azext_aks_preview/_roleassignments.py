# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.command_modules.acs._roleassignments import (
    add_role_assignment,
    add_role_assignment_executor,
)


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
        is_service_principal=is_service_principal,
        delay=delay,
        scope=scope,
        assignee_principal_type=assignee_principal_type,
    )


def add_role_assignment_executor(
    cmd,
    role,
    assignee,
    resource_group_name=None,
    scope=None,
    resolve_assignee=True,
    assignee_principal_type=None,
):
    return add_role_assignment_executor(
        cmd,
        role,
        assignee,
        resource_group_name=resource_group_name,
        scope=scope,
        resolve_assignee=resolve_assignee,
        assignee_principal_type=assignee_principal_type,
    )
