# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re
from uuid import UUID

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.cli.core.aaz import AAZCommand, AAZIntArg, AAZIntArgFormat, AAZStrArg, has_value, register_command
from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.cli.core.commands.command_operation import WaitCommandOperation
from azure.mgmt.core.tools import is_valid_resource_id, parse_resource_id
from knack.log import get_logger
from knack.util import CLIError

from .aaz.latest.monitor.account.trace_container import Create as _TraceContainerCreate
from .aaz.latest.monitor.account.trace_container import Show as _TraceContainerShow
from .aaz.latest.monitor.account.trace_container import Update as _TraceContainerUpdate
from .aaz.latest.monitor.trace_association import resource as _ResourceAssociations
from .aaz.latest.monitor.trace_association import resource_group as _ResourceGroupAssociations
from .aaz.latest.monitor.trace_association import subscription as _SubscriptionAssociations


logger = get_logger(__name__)
_CONTAINER_DEFAULTS = {
    "traceRetentionInDays": 30,
    "traceDurationWindowInSeconds": 600,
    "traceMetricsState": "Enabled",
}
_CONTAINER_ARGUMENTS = {
    "retention_days": "traceRetentionInDays",
    "trace_duration_window": "traceDurationWindowInSeconds",
    "trace_metrics": "traceMetricsState",
}
_SCOPE_PATTERN = re.compile(
    r"/subscriptions/(?P<subscription>[^/]+)"
    r"(?:/resourceGroups/(?P<resource_group>[^/]+)"
    r"(?:/providers/Microsoft\.Insights/components/(?P<resource_name>[^/]+))?)?",
    re.IGNORECASE,
)
_ASSOCIATION_SUFFIX = re.compile(r"/providers/microsoft\.monitor/traceassociations/default/?$", re.IGNORECASE)


def _workspace_arguments(workspace_id):
    if not is_valid_resource_id(workspace_id):
        raise InvalidArgumentValueError("Specify an Azure Monitor workspace resource ID.")
    parts = parse_resource_id(workspace_id)
    if (parts["resource_namespace"].lower() != "microsoft.monitor"
            or parts["resource_type"].lower() != "accounts" or parts["resource_parent"]):
        raise InvalidArgumentValueError("The trace workspace must be a Microsoft.Monitor/accounts resource.")
    try:
        UUID(parts["subscription"])
    except ValueError as error:
        raise InvalidArgumentValueError("The trace workspace resource ID must contain a subscription ID.") from error
    return {
        "subscription": parts["subscription"],
        "resource_group": parts["resource_group"],
        "azure_monitor_workspace_name": parts["name"],
    }


def _get_container(cli_ctx, workspace_arguments):
    try:
        container = _TraceContainerShow(cli_ctx=cli_ctx)(command_args=workspace_arguments)
    except ResourceNotFoundError:
        return None
    _container_settings(container)
    return container


def _container_settings(container):
    if container is None:
        raise CLIError("The trace container API returned no resource. Inspect the workspace before retrying.")
    properties = container.get("properties", {})
    missing = _CONTAINER_DEFAULTS.keys() - properties.keys()
    if missing:
        raise CLIError(
            "The trace container response is missing required settings: {}.".format(", ".join(sorted(missing)))
        )
    settings = {name: properties[name] for name in _CONTAINER_DEFAULTS}
    try:
        if settings["traceRetentionInDays"] is None or settings["traceMetricsState"] is None:
            raise InvalidArgumentValueError("Required settings cannot be null.")
        _validate_trace_settings(settings["traceRetentionInDays"], settings["traceMetricsState"])
        duration = settings["traceDurationWindowInSeconds"]
        if not isinstance(duration, int) or isinstance(duration, bool) or not 120 <= duration <= 600:
            raise InvalidArgumentValueError("The duration window must be between 120 and 600 seconds.")
    except InvalidArgumentValueError as error:
        raise CLIError("The trace container returned invalid settings: {}.".format(error)) from error
    return settings


def _optional(value):
    return value.to_serialized_data() if has_value(value) else None


def _validate_trace_settings(retention_days, trace_metrics):
    if retention_days is not None and (
            not isinstance(retention_days, int) or isinstance(retention_days, bool) or not 4 <= retention_days <= 730):
        raise InvalidArgumentValueError("Trace retention must be an integer between 4 and 730 days.")
    if trace_metrics is not None and trace_metrics not in ("Enabled", "Disabled"):
        raise InvalidArgumentValueError("Trace metrics must be Enabled or Disabled.")


def _container_command(workspace_id):
    args = _workspace_arguments(workspace_id)
    return (
        'az monitor account trace-container create --subscription "{}" -g "{}" -w "{}"'
        .format(args["subscription"], args["resource_group"], args["azure_monitor_workspace_name"])
    )


def _ensure_container(cli_ctx, workspace_id, retention_days=None, trace_metrics=None):
    _validate_trace_settings(retention_days, trace_metrics)
    arguments = _workspace_arguments(workspace_id)
    container = _get_container(cli_ctx, arguments)
    created = container is None
    if container is not None and container.get("properties", {}).get("provisioningState") not in (None, "Succeeded"):
        def read_container(**kwargs):
            return _TraceContainerShow(cli_ctx=cli_ctx)(command_args=kwargs)

        result = WaitCommandOperation.wait(
            command_args={
                **arguments, "timeout": 1800, "interval": 5, "created": True,
                "deleted": False, "updated": False, "exists": False, "custom": None,
            },
            cli_ctx=cli_ctx,
            getter=read_container,
        )
        if isinstance(result, CLIError):
            raise result
        container = _TraceContainerShow(cli_ctx=cli_ctx)(command_args=arguments)
    settings = dict(_CONTAINER_DEFAULTS) if created else _container_settings(container)
    requested = {"traceRetentionInDays": retention_days, "traceMetricsState": trace_metrics}
    for name, value in requested.items():
        if value is None:
            continue
        if container is not None and value != settings[name]:
            raise InvalidArgumentValueError(
                "The existing trace container has {}={}. Onboarding does not modify shared settings. "
                "Use az monitor account trace-container update to change them.".format(name, settings[name])
            )
        settings[name] = value
    if created:
        try:
            container = _TraceContainerCreate(cli_ctx=cli_ctx)(command_args={
                **arguments,
                **{argument: settings[name] for argument, name in _CONTAINER_ARGUMENTS.items()},
            }).result()
        except HttpResponseError as error:
            if error.status_code == 403:
                raise CLIError(
                    "You cannot create a trace container on {}. Ask the workspace owner to run:\n  {}"
                    .format(workspace_id, _container_command(workspace_id))
                ) from error
            raise
        settings = _container_settings(container)
    logger.warning(
        "%s trace container on %s: retention %s days, trace metrics %s.",
        "Created" if created else "Using existing", workspace_id,
        settings["traceRetentionInDays"], settings["traceMetricsState"],
    )
    return container


def _scope_arguments(scope):
    match = _SCOPE_PATTERN.fullmatch(scope.rstrip("/"))
    if match is None:
        raise InvalidArgumentValueError(
            "--resource-uri must be a subscription, resource group, or Application Insights component resource ID."
        )
    arguments = {key: value for key, value in match.groupdict().items() if value is not None}
    try:
        UUID(arguments["subscription"])
    except ValueError as error:
        raise InvalidArgumentValueError("The scope must contain a subscription ID, not a subscription name.") from error
    if "resource_name" in arguments:
        arguments.update(provider_name="Microsoft.Insights", provider_type="components")
        return _ResourceAssociations, arguments
    if "resource_group" in arguments:
        return _ResourceGroupAssociations, arguments
    return _SubscriptionAssociations, arguments


def _association_scope(association):
    scope = _ASSOCIATION_SUFFIX.sub("", association.get("id", ""))
    if not scope or scope == association.get("id"):
        raise CLIError("The trace association response is missing a valid scope resource ID.")
    return scope


def _list_associations(cli_ctx, scope):
    operations, arguments = _scope_arguments(scope)
    return list(operations.List(cli_ctx=cli_ctx)(command_args=arguments))


def _destinations(associations):
    destinations = {}
    for association in associations:
        workspace_id = association.get("properties", {}).get("azureMonitorWorkspaceResourceId")
        if not workspace_id:
            raise CLIError("The trace association response is missing its Azure Monitor workspace resource ID.")
        key = workspace_id.rstrip("/").lower()
        entry = destinations.setdefault(key, {"workspace": workspace_id, "scopes": []})
        entry["scopes"].append(_association_scope(association))
    return list(destinations.values())


def _report_destinations(scope, associations):
    destinations = _destinations(associations)
    if not destinations:
        logger.warning("No trace associations apply to %s.", scope)
        return
    logger.warning("Traces for %s route to:", scope)
    for destination in destinations:
        logger.warning("  %s via %s", destination["workspace"], ", ".join(destination["scopes"]))


def _put_association(cli_ctx, scope, workspace_id):
    operations, arguments = _scope_arguments(scope)
    try:
        return operations.Create(cli_ctx=cli_ctx)(command_args={
            **arguments, "azure_monitor_workspace": workspace_id,
        })
    except HttpResponseError as error:
        details = str(error)
        if getattr(getattr(error, "error", None), "code", None) == "UnsupportedLocation":
            details = "The backing Log Analytics workspace region is not enabled for traces. " + details
        raise CLIError(
            "The trace container is ready on {}, but writing the association on {} failed: {}. "
            "Re-run the same command once resolved.".format(workspace_id, scope, details)
        ) from error


def _replace_association(associations, scope, replacement):
    return [
        association for association in associations
        if _association_scope(association).lower() != scope.rstrip("/").lower()
    ] + [replacement]


def _report_association_update(scope, associations, replacement):
    for association in associations:
        if _association_scope(association).lower() == scope.rstrip("/").lower():
            old = association["properties"]["azureMonitorWorkspaceResourceId"]
            new = replacement["properties"]["azureMonitorWorkspaceResourceId"]
            if old.rstrip("/").lower() != new.rstrip("/").lower():
                logger.warning("Replaced the trace destination at %s: %s -> %s. Ancestor associations are unchanged.",
                               scope, old, new)
    _report_destinations(scope, _replace_association(associations, scope, replacement))


def _create_association(cli_ctx, scope, workspace_id, retention_days=None, trace_metrics=None):
    _validate_trace_settings(retention_days, trace_metrics)
    _workspace_arguments(workspace_id)
    associations = _list_associations(cli_ctx, scope)
    _ensure_container(cli_ctx, workspace_id, retention_days, trace_metrics)
    result = _put_association(cli_ctx, scope, workspace_id)
    _report_association_update(scope, associations, result)
    return result


def _delete_association(cli_ctx, scope):
    operations, arguments = _scope_arguments(scope)
    try:
        operations.Delete(cli_ctx=cli_ctx)(command_args=arguments)
    except ResourceNotFoundError:
        logger.warning("No trace association was configured at %s.", scope)
    else:
        logger.warning("Removed the trace association at %s.", scope)
    try:
        remaining = _list_associations(cli_ctx, scope)
    except HttpResponseError as error:
        raise CLIError(
            "The association at {} is removed, but reading remaining destinations failed: {}."
            .format(scope, error)
        ) from error
    _report_destinations(scope, remaining)


class TraceContainerCreate(_TraceContainerCreate):
    def pre_operations(self):
        args = self.ctx.args
        _validate_trace_settings(_optional(args.retention_days), _optional(args.trace_metrics))
        workspace_arguments = {
            "subscription": self.ctx.subscription_id,
            "resource_group": args.resource_group.to_serialized_data(),
            "azure_monitor_workspace_name": args.azure_monitor_workspace_name.to_serialized_data(),
        }
        container = _get_container(self.cli_ctx, workspace_arguments)
        settings = dict(_CONTAINER_DEFAULTS) if container is None else _container_settings(container)
        for argument, property_name in _CONTAINER_ARGUMENTS.items():
            value = getattr(args, argument)
            if not has_value(value):
                setattr(args, argument, settings[property_name])

    def post_operations(self):
        _container_settings(self._output())


class TraceContainerUpdate(_TraceContainerUpdate):
    def post_operations(self):
        _container_settings(self._output())


class _TraceAssociationCommand(AAZCommand):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        schema = super()._build_arguments_schema(*args, **kwargs)
        schema.resource_uri = AAZStrArg(
            options=["--resource-uri"], required=True,
            help="Resource ID of a subscription, resource group, or Application Insights component.",
        )
        return schema


@register_command("monitor trace-association create", is_preview=True)
class TraceAssociationCreate(_TraceAssociationCommand):
    """Route traces from a scope to an Azure Monitor workspace, creating its trace container if needed.

    :example: Onboard a resource group
        az monitor trace-association create --resource-uri <scope-id> --azure-monitor-workspace <amw-id>
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        schema = super()._build_arguments_schema(*args, **kwargs)
        schema.azure_monitor_workspace = AAZStrArg(
            options=["--azure-monitor-workspace", "-w"], required=True, help="Azure Monitor workspace resource ID.",
        )
        schema.trace_retention_days = AAZIntArg(
            options=["--trace-retention-days"], help="Retention for a new container. Default: 30 days.",
            fmt=AAZIntArgFormat(minimum=4, maximum=730),
        )
        schema.trace_metrics = AAZStrArg(
            options=["--trace-metrics"], enum={"Enabled": "Enabled", "Disabled": "Disabled"},
            help="Trace-derived metrics for a new container. Default: Enabled. Metrics are billed.",
        )
        return schema

    def _handler(self, command_args):
        super()._handler(command_args)
        args = self.ctx.args
        return _create_association(
            self.cli_ctx, args.resource_uri.to_serialized_data(),
            args.azure_monitor_workspace.to_serialized_data(),
            _optional(args.trace_retention_days), _optional(args.trace_metrics),
        )


@register_command("monitor trace-association show", is_preview=True)
class TraceAssociationShow(_TraceAssociationCommand):
    """Show the association configured at exactly this scope, excluding inherited associations.

    :example: Show a scope's own association
        az monitor trace-association show --resource-uri <scope-id>
    """

    def _handler(self, command_args):
        super()._handler(command_args)
        operations, arguments = _scope_arguments(self.ctx.args.resource_uri.to_serialized_data())
        return operations.Show(cli_ctx=self.cli_ctx)(command_args=arguments)


@register_command("monitor trace-association list", is_preview=True)
class TraceAssociationList(_TraceAssociationCommand):
    """List associations applying to this scope, including resource group and subscription ancestors.

    :example: Show every association applying to an Application Insights component
        az monitor trace-association list --resource-uri <component-id>
    """

    def _handler(self, command_args):
        super()._handler(command_args)
        return _list_associations(self.cli_ctx, self.ctx.args.resource_uri.to_serialized_data())


@register_command("monitor trace-association delete", is_preview=True)
class TraceAssociationDelete(_TraceAssociationCommand):
    """Remove this scope's association without deleting its trace container or ancestor associations.

    :example: Remove routing configured at a resource group
        az monitor trace-association delete --resource-uri <resource-group-id>
    """

    def _handler(self, command_args):
        super()._handler(command_args)
        _delete_association(self.cli_ctx, self.ctx.args.resource_uri.to_serialized_data())
