# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.core.breaking_change import (
    register_argument_deprecate,
    register_required_flag_breaking_change,
)

register_argument_deprecate(
    "networkfabric bootstrapinterface list",
    "--network-bootstrap-device-name",
    target_version="10.0.x",
)
register_argument_deprecate(
    "networkfabric bootstrapinterface show",
    "--network-bootstrap-device-name",
    target_version="10.0.x",
)
register_argument_deprecate(
    "networkfabric bootstrapinterface wait",
    "--network-bootstrap-device-name",
    target_version="10.0.x",
)
register_required_flag_breaking_change(
    "networkfabric bootstrapinterface list",
    "--bootstrap-device",
    target_version="10.0.x",
)
register_required_flag_breaking_change(
    "networkfabric bootstrapinterface show",
    "--bootstrap-device",
    target_version="10.0.x",
)
register_required_flag_breaking_change(
    "networkfabric bootstrapinterface wait",
    "--bootstrap-device",
    target_version="10.0.x",
)
