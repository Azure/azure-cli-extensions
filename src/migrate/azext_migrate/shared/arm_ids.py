# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Generic ARM resource-id and URL builders shared across features."""

from azext_migrate.shared import constants


def migrate_project_id(subscription_id, resource_group, project_name):
    """Build a migrate-project ARM id."""
    return constants.MIGRATE_PROJECT_ID_TEMPLATE.format(
        subscription_id=subscription_id,
        resource_group=resource_group,
        project_name=project_name,
    )


def runbook_id(project_id, runbook_name):
    """Build a runbook ARM id from a project id."""
    return constants.RUNBOOK_ID_TEMPLATE.format(
        project_id=project_id, runbook_name=runbook_name)


def execution_id(runbook_resource_id, execution):
    """Build a runbook-execution ARM id from a runbook id."""
    return constants.EXECUTION_ID_TEMPLATE.format(
        runbook_id=runbook_resource_id, execution_id=execution)


def artifact_id(project_id, artifact_name):
    """Build an artifact ARM id from a project id."""
    return constants.ARTIFACT_ID_TEMPLATE.format(
        project_id=project_id, artifact_name=artifact_name)


def with_api_version(resource_id, api_version):
    """Append the api-version query parameter to a resource id/url."""
    joiner = '&' if '?' in resource_id else '?'
    return f"{resource_id}{joiner}api-version={api_version}"
