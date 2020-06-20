# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

import os

from .operations.workspace import WorkspaceInfo
from .operations.target import TargetInfo


def validate_workspace_info(cmd, namespace):
    """
    Makes sure all parameters for a workspace are available.
    """
    group = getattr(namespace, 'resource_group_name', None)
    name = getattr(namespace, 'workspace_name', None)
    ws = WorkspaceInfo(cmd, group, name)

    if not ws.subscription:
        raise ValueError("Missing subscription argument")
    if not ws.resource_group:
        raise ValueError("Missing resource-group argument")
    if not ws.name:
        raise ValueError("Missing workspace-name argument")


def validate_target_info(cmd, namespace):
    """
    Makes sure all parameters for a target are available.
    """
    target_id = getattr(namespace, 'target_id', None)
    target = TargetInfo(cmd, target_id)

    if not target.target_id:
        raise ValueError("Missing target-id argument")


def validate_workspace_and_target_info(cmd, namespace):
    """
    Makes sure all parameters for both, a workspace and a target are available.
    """
    validate_workspace_info(cmd, namespace)
    validate_target_info(cmd, namespace)
