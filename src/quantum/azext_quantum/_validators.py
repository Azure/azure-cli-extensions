# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long,unused-argument

from .operations.workspace import WorkspaceInfo
from .operations.target import TargetInfo


def validate_workspace_internal(cmd, namespace, require_location):
    """
    Internal implementation to validate workspace info parameters with an optional location
    """
    group = getattr(namespace, 'resource_group_name', None)
    name = getattr(namespace, 'workspace_name', None)
    location = getattr(namespace, 'location', None)
    ws = WorkspaceInfo(cmd, group, name, location)

    if not ws.subscription:
        raise ValueError("Missing subscription argument")
    if not ws.resource_group:
        raise ValueError("Missing resource-group argument")
    if not ws.name:
        raise ValueError("Missing workspace-name argument")
    if require_location and not ws.location:
        raise ValueError("Missing location argument")


def validate_workspace_info(cmd, namespace):
    """
    Makes sure all parameters for a workspace are available including location.
    """
    validate_workspace_internal(cmd, namespace, True)


def validate_workspace_info_no_location(cmd, namespace):
    """
    Makes sure all parameters for a workspace are available, not including location.
    """
    validate_workspace_internal(cmd, namespace, False)


def validate_target_info(cmd, namespace):
    """
    Makes sure all parameters for a target are available.
    """
    target_id = getattr(namespace, 'target_id', None)
    target = TargetInfo(cmd, target_id)

    if not target.target_id:
        # raise ValueError("Missing target-id argument.  Use `az quantum target set -t MyTarget` to set a default Target ID.")
        raise ValueError("No default Target ID has been saved.  Use `az quantum target set -t MyTarget` to set a default Target ID.")


def validate_workspace_and_target_info(cmd, namespace):
    """
    Makes sure all parameters for both, a workspace and a target are available.
    """
    validate_workspace_info(cmd, namespace)
    validate_target_info(cmd, namespace)


def validate_provider_and_sku_info(cmd, namespace):
    """
    Makes sure all parameters for quantum offering operations are present.
    """
    provider_id = getattr(namespace, 'provider_id', None)
    sku = getattr(namespace, 'sku', None)
    location = getattr(namespace, 'location', None)
    if not provider_id:
        raise ValueError("Missing provider id argument")
    if not sku:
        raise ValueError("Missing sku argument")
    if not location:
        raise ValueError("Missing location argument")
