# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.core.exceptions import ResourceNotFoundError
from azure.cli.core.aaz import has_value
from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.mgmt.core.tools import is_valid_resource_id, parse_resource_id
from knack.util import CLIError

from .aaz.latest.monitor.account.trace_container import Create as _TraceContainerCreate
from .aaz.latest.monitor.account.trace_container import Show as _TraceContainerShow


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


def _workspace_arguments(workspace_id):
    if not is_valid_resource_id(workspace_id):
        raise InvalidArgumentValueError("Specify an Azure Monitor workspace resource ID.")
    parts = parse_resource_id(workspace_id)
    if (parts["resource_namespace"].lower() != "microsoft.monitor"
            or parts["resource_type"].lower() != "accounts" or parts["resource_parent"]):
        raise InvalidArgumentValueError("The trace workspace must be a Microsoft.Monitor/accounts resource.")
    return {
        "subscription": parts["subscription"],
        "resource_group": parts["resource_group"],
        "azure_monitor_workspace_name": parts["name"],
    }


def _get_container(cli_ctx, workspace_arguments):
    try:
        return _TraceContainerShow(cli_ctx=cli_ctx)(command_args=workspace_arguments)
    except ResourceNotFoundError:
        return None


def _container_settings(container):
    if container is None:
        return dict(_CONTAINER_DEFAULTS)
    properties = container.get("properties", {})
    missing = _CONTAINER_DEFAULTS.keys() - properties.keys()
    if missing:
        raise CLIError(
            "The trace container response is missing required settings: {}.".format(", ".join(sorted(missing)))
        )
    return {name: properties[name] for name in _CONTAINER_DEFAULTS}


class TraceContainerCreate(_TraceContainerCreate):
    def pre_operations(self):
        args = self.ctx.args
        if has_value(args.trace_metrics) and args.trace_metrics.to_serialized_data() not in ("Enabled", "Disabled"):
            raise InvalidArgumentValueError("--trace-metrics must be Enabled or Disabled.")
        workspace_arguments = {
            "subscription": self.ctx.subscription_id,
            "resource_group": args.resource_group.to_serialized_data(),
            "azure_monitor_workspace_name": args.azure_monitor_workspace_name.to_serialized_data(),
        }
        settings = _container_settings(_get_container(self.cli_ctx, workspace_arguments))
        for argument, property_name in _CONTAINER_ARGUMENTS.items():
            value = getattr(args, argument)
            if not has_value(value):
                setattr(args, argument, settings[property_name])
