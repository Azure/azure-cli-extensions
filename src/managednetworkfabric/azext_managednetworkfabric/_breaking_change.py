# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.core.breaking_change import (
    register_argument_deprecate,
    register_command_deprecate,
)

register_command_deprecate(
    "networkfabric device refresh-configuration",
    redirect="networkfabric device refresh-config",
    target_version="10.0.x",
)
register_command_deprecate(
    "networkfabric fabric commit-configuration",
    redirect="networkfabric fabric commit-config",
    target_version="10.0.x",
)
register_command_deprecate(
    "networkfabric fabric validate-configuration",
    redirect="networkfabric fabric validate-config",
    target_version="10.0.x",
)
register_command_deprecate(
    "networkfabric fabric view-device-configuration",
    redirect="networkfabric fabric view-device-config",
    target_version="10.0.x",
)
register_argument_deprecate(
    "networkfabric bootstrapinterface list",
    "--network-bootstrap-device-name",
    redirect="--bootstrap-device",
    target_version="10.0.x",
)
register_argument_deprecate(
    "networkfabric bootstrapinterface show",
    "--network-bootstrap-device-name",
    redirect="--bootstrap-device",
    target_version="10.0.x",
)
register_argument_deprecate(
    "networkfabric bootstrapinterface wait",
    "--network-bootstrap-device-name",
    redirect="--bootstrap-device",
    target_version="10.0.x",
)
register_argument_deprecate(
    "networkfabric device reboot",
    "--network-device-name",
    redirect="--resource-name",
    target_version="10.0.x",
)
register_argument_deprecate(
    "networkfabric device refresh-config",
    "--network-device-name",
    redirect="--resource-name",
    target_version="10.0.x",
)
register_argument_deprecate(
    "networkfabric fabric view-device-config",
    "--network-fabric-name",
    redirect="--resource-name",
    target_version="10.0.x",
)
register_argument_deprecate(
    "networkfabric fabric commit-batch-status",
    "--network-fabric-name",
    redirect="--resource-name",
    target_version="10.0.x",
)
register_argument_deprecate(
    "networkfabric fabric discard-commit-batch",
    "--network-fabric-name",
    redirect="--resource-name",
    target_version="10.0.x",
)
register_argument_deprecate(
    "networkfabric fabric lock-fabric",
    "--network-fabric-name",
    redirect="--resource-name",
    target_version="10.0.x",
)
register_argument_deprecate(
    "networkfabric fabric resync-certificate",
    "--network-fabric-name",
    redirect="--resource-name",
    target_version="10.0.x",
)
register_argument_deprecate(
    "networkfabric fabric resync-password",
    "--network-fabric-name",
    redirect="--resource-name",
    target_version="10.0.x",
)
register_argument_deprecate(
    "networkfabric fabric rotate-certificate",
    "--network-fabric-name",
    redirect="--resource-name",
    target_version="10.0.x",
)
register_argument_deprecate(
    "networkfabric fabric rotate-password",
    "--network-fabric-name",
    redirect="--resource-name",
    target_version="10.0.x",
)
register_argument_deprecate(
    "networkfabric networkmonitor create",
    "-n",
    redirect="--resource-name",
    target_version="10.0.x",
)
register_argument_deprecate(
    "networkfabric networkmonitor create",
    "--name",
    redirect="--resource-name",
    target_version="10.0.x",
)
register_argument_deprecate(
    "networkfabric networkmonitor create",
    "--network-monitor-name",
    redirect="--resource-name",
    target_version="10.0.x",
)
register_argument_deprecate(
    "networkfabric networkmonitor delete",
    "-n",
    redirect="--resource-name",
    target_version="10.0.x",
)
register_argument_deprecate(
    "networkfabric networkmonitor delete",
    "--name",
    redirect="--resource-name",
    target_version="10.0.x",
)
register_argument_deprecate(
    "networkfabric networkmonitor delete",
    "--network-monitor-name",
    redirect="--resource-name",
    target_version="10.0.x",
)
register_argument_deprecate(
    "networkfabric networkmonitor show",
    "-n",
    redirect="--resource-name",
    target_version="10.0.x",
)
register_argument_deprecate(
    "networkfabric networkmonitor show",
    "--name",
    redirect="--resource-name",
    target_version="10.0.x",
)
register_argument_deprecate(
    "networkfabric networkmonitor show",
    "--network-monitor-name",
    redirect="--resource-name",
    target_version="10.0.x",
)
register_argument_deprecate(
    "networkfabric networkmonitor update",
    "-n",
    redirect="--resource-name",
    target_version="10.0.x",
)
register_argument_deprecate(
    "networkfabric networkmonitor update",
    "--name",
    redirect="--resource-name",
    target_version="10.0.x",
)
register_argument_deprecate(
    "networkfabric networkmonitor update",
    "--network-monitor-name",
    redirect="--resource-name",
    target_version="10.0.x",
)
register_argument_deprecate(
    "networkfabric networkmonitor wait",
    "-n",
    redirect="--resource-name",
    target_version="10.0.x",
)
register_argument_deprecate(
    "networkfabric networkmonitor wait",
    "--name",
    redirect="--resource-name",
    target_version="10.0.x",
)
register_argument_deprecate(
    "networkfabric networkmonitor wait",
    "--network-monitor-name",
    redirect="--resource-name",
    target_version="10.0.x",
)
register_argument_deprecate(
    "networkfabric tap resync",
    "--network-tap-name",
    redirect="--resource-name",
    target_version="10.0.x",
)
