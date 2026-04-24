# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: skip-file
# flake8: noqa

from azure.cli.core.aaz import *


@register_command_group(
    "workload-orchestration cluster",
)
class __CMDGroup(AAZCommandGroup):
    """Prepare an Arc-connected Kubernetes cluster for Workload Orchestration."""
    pass


__all__ = ["__CMDGroup"]
