# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import NamedTuple, Optional

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.cli.core.commands.client_factory import get_mgmt_service_client, get_subscription_id
from azure.cli.core.profiles import ResourceType
from azure.mgmt.core.tools import resource_id
from knack.log import get_logger
from knack.util import CLIError

from ._trace import (
    _association_scope, _delete_association, _destinations, _ensure_container, _get_container,
    _list_associations, _put_association, _report_association_update, _report_destinations,
    _scope_arguments, _validate_trace_settings, _workspace_arguments, _container_command,
)


logger = get_logger(__name__)


class _Onboarding(NamedTuple):
    scope: str
    workspace: Optional[str]
    associations: list
    associate: bool


def validate_component_trace_options(enable_traces=None, disable_traces=None, trace_workspace=None,
                                     trace_retention_days=None, trace_metrics=None):
    _validate_trace_settings(trace_retention_days, trace_metrics)
    if trace_workspace is not None and not trace_workspace.strip():
        raise InvalidArgumentValueError("--trace-workspace cannot be empty.")
    if trace_workspace is not None and trace_workspace.startswith("/"):
        _workspace_arguments(trace_workspace)
    if disable_traces and (enable_traces or trace_workspace is not None
                           or trace_retention_days is not None or trace_metrics is not None):
        raise InvalidArgumentValueError("--disable-traces cannot be combined with other trace options.")
    if (trace_retention_days is not None or trace_metrics is not None) and not (enable_traces or trace_workspace):
        raise InvalidArgumentValueError(
            "--trace-retention-days and --trace-metrics require --enable-traces or --trace-workspace."
        )


def _get_component(cli_ctx, resource_group_name, application, allow_missing):
    from ._client_factory import applicationinsights_mgmt_plane_client
    client = applicationinsights_mgmt_plane_client(cli_ctx, api_version="2020-02-02-preview").components
    try:
        return client.get(resource_group_name, application)
    except HttpResponseError as error:
        if allow_missing and error.status_code == 404:
            return None
        raise


def _resolve_workspace(scope, workspace):
    if workspace.startswith("/"):
        _workspace_arguments(workspace)
        return workspace
    if "/" in workspace:
        raise InvalidArgumentValueError("Specify an Azure Monitor workspace name or full resource ID.")
    _, source = _scope_arguments(scope)
    return resource_id(
        subscription=source["subscription"], resource_group=source["resource_group"],
        namespace="Microsoft.Monitor", type="accounts", name=workspace,
    )


def _resolve_default_workspace(cli_ctx, scope, location):
    if not location:
        raise CLIError("Cannot determine the Application Insights location for a default trace workspace.")
    _, source = _scope_arguments(scope)
    client = get_mgmt_service_client(
        cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES, subscription_id=source["subscription"],
    )
    provider = client.providers.get("Microsoft.Monitor")
    locations = [
        region.lower().replace(" ", "")
        for resource_type in provider.resource_types if resource_type.resource_type.lower() == "accounts"
        for region in (resource_type.locations or [])
    ]
    location = location.lower().replace(" ", "")
    if location == "centraluseuap":
        region = "eastus2euap"
    elif location in locations:
        region = location
    elif locations:
        region = locations[0]
    elif cli_ctx.cloud.name == "AzureCloud":
        region = "eastus"
    else:
        raise CLIError("Microsoft.Monitor/accounts has no supported locations in the active cloud.")
    group = "DefaultResourceGroup-" + region
    name = ("DefaultAzureMonitorWorkspace-" + region)[:43]
    workspace = resource_id(
        subscription=source["subscription"], resource_group=group,
        namespace="Microsoft.Monitor", type="accounts", name=name,
    )
    if not client.resource_groups.check_existence(group):
        client.resource_groups.create_or_update(group, {"location": region})
    try:
        try:
            client.resources.get_by_id(workspace, "2023-04-03")
        except ResourceNotFoundError:
            client.resources.begin_create_or_update_by_id(
                workspace, "2023-04-03", {"location": region, "properties": {}},
            ).result()
    except HttpResponseError as error:
        raise CLIError(
            "Default resource group {} is available, but preparing workspace {} failed: {}. "
            "The resource group is reusable; retry once resolved.".format(group, workspace, error)
        ) from error
    return workspace


def _check_inherited_containers(cli_ctx, associations):
    for destination in _destinations(associations):
        workspace = destination["workspace"]
        container = _get_container(cli_ctx, _workspace_arguments(workspace))
        if container is None:
            logger.warning(
                "The inherited workspace %s has no trace container; nothing is being stored there. Run:\n  %s",
                workspace, _container_command(workspace),
            )
        elif container.get("properties", {}).get("provisioningState") not in (None, "Succeeded"):
            logger.warning("The trace container on inherited workspace %s is not ready.", workspace)


def _prepare_onboarding(cli_ctx, scope, location, options, creating):
    source_scope = scope.rsplit("/providers/", 1)[0] if creating else scope
    associations = _list_associations(cli_ctx, source_scope)
    workspace = options.get("trace_workspace")
    if workspace:
        workspace = _resolve_workspace(scope, workspace)
        associate = True
    else:
        own = next((
            association for association in associations if _association_scope(association).lower() == scope.lower()
        ), None)
        if own is not None:
            workspace = own["properties"]["azureMonitorWorkspaceResourceId"]
            associate = False
        elif associations:
            if options.get("trace_retention_days") is not None or options.get("trace_metrics") is not None:
                raise InvalidArgumentValueError(
                    "This component inherits its trace workspaces. Specify --trace-workspace to select a container "
                    "for trace settings; inherited containers are not modified."
                )
            _check_inherited_containers(cli_ctx, associations)
            return _Onboarding(scope, None, associations, False)
        else:
            workspace = _resolve_default_workspace(cli_ctx, scope, location)
            associate = True
    _ensure_container(
        cli_ctx, workspace, options.get("trace_retention_days"), options.get("trace_metrics"),
    )
    return _Onboarding(scope, workspace, associations, associate)


def _complete_onboarding(cli_ctx, plan, operation):
    associations = plan.associations
    if plan.associate:
        try:
            association = _put_association(cli_ctx, plan.scope, plan.workspace)
        except CLIError as error:
            _, source = _scope_arguments(plan.scope)
            raise CLIError(
                "Component {} was {}, but enabling traces failed: {}\nRetry:\n"
                '  az monitor app-insights component update --subscription "{}" -g "{}" -a "{}" '
                '--enable-traces --trace-workspace "{}"'.format(
                    source["resource_name"], operation, error, source["subscription"],
                    source["resource_group"], source["resource_name"], plan.workspace,
                )
            ) from error
        _report_association_update(plan.scope, associations, association)
    else:
        _report_destinations(plan.scope, associations)


def run_component_operation(cmd, application, resource_group_name, write_component, component_arguments,
                            trace_options, creating=False):
    validate_component_trace_options(**trace_options)
    if not (trace_options.get("enable_traces") or trace_options.get("disable_traces")
            or trace_options.get("trace_workspace")):
        return write_component(**component_arguments)
    if (component_arguments.get("workspace_resource_id") is not None
            and component_arguments.get("retention_in_days") is not None):
        raise CLIError("Retention time can be set only when Application Insights is not connected "
                       "to a Log Analytics workspace.")
    component = _get_component(cmd.cli_ctx, resource_group_name, application, allow_missing=creating)
    was_missing = component is None
    scope = resource_id(
        subscription=get_subscription_id(cmd.cli_ctx), resource_group=resource_group_name,
        namespace="Microsoft.Insights", type="components", name=application,
    )
    changed = creating or any(value is not None for value in component_arguments.values())
    if trace_options.get("disable_traces"):
        if changed:
            component = write_component(**component_arguments)
        _delete_association(cmd.cli_ctx, scope)
        return component
    plan = _prepare_onboarding(
        cmd.cli_ctx, scope, component_arguments.get("location") or getattr(component, "location", None),
        trace_options, creating=was_missing,
    )
    try:
        if changed:
            component = write_component(**component_arguments)
    except (HttpResponseError, CLIError) as error:
        if plan.workspace is None:
            raise
        raise CLIError(
            "Trace container is ready on {}, but writing component {} failed: {}. "
            "The container is reusable. Re-run the same command once resolved."
            .format(plan.workspace, application, error)
        ) from error
    _complete_onboarding(cmd.cli_ctx, plan, "created" if was_missing else "updated")
    return component
