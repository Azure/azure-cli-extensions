# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long,unused-argument

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
        # raise ValueError("Missing target-id argument.  Use `az quantum target set -t MyTarget` to set a default Target ID.")
        raise ValueError("No default Target ID has been saved.  Use `az quantum target set -t MyTarget` to set a default Target ID.")


def validate_workspace_and_target_info(cmd, namespace):
    """
    Makes sure all parameters for both, a workspace and a target are available.
    """
    validate_workspace_info(cmd, namespace)
    validate_target_info(cmd, namespace)


def validate_target_list_info(cmd, namespace):
    """
    Validate parameters for `az quantum target list`, which supports either a workspace context
    (default) or a provider-account context via --provider-id. The two are mutually exclusive.
    """
    from azure.cli.core.azclierror import MutuallyExclusiveArgumentError

    provider_id = getattr(namespace, 'provider_id', None)
    if provider_id:
        workspace_name = getattr(namespace, 'workspace_name', None)
        # A configured default workspace should not trigger the mutual-exclusion error, so only
        # treat an explicitly-provided workspace name (one that differs from the saved default)
        # as a conflict.
        default_workspace = cmd.cli_ctx.config.get(cmd.cli_ctx.config.defaults_section_name, 'workspace', None)
        if workspace_name and workspace_name != default_workspace:
            raise MutuallyExclusiveArgumentError(
                "Specify either --provider-id/-p or --workspace-name/-w, not both.")
        return
    validate_workspace_info(cmd, namespace)


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
