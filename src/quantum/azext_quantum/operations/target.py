# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long,redefined-builtin

from .._client_factory import cf_providers
from .workspace import WorkspaceInfo


class TargetInfo:
    def __init__(self, cmd, target_id=None):

        def select_value(key, value):
            if value is not None:
                return value
            value = cmd.cli_ctx.config.get(cmd.cli_ctx.config.defaults_section_name, key, None)
            return value

        self.target_id = select_value('target_id', target_id)

    def clear(self):
        self.target_id = ''

    def save(self, cmd):
        from azure.cli.core.util import ConfiguredDefaultSetter

        with ConfiguredDefaultSetter(cmd.cli_ctx.config, False):
            cmd.cli_ctx.config.set_value(cmd.cli_ctx.config.defaults_section_name, 'target_id', self.target_id)


def get(cmd, target_id=None):
    """
    Get the details of the given (or current) target to use when submitting jobs to Azure Quantum.
    """
    info = TargetInfo(cmd, target_id)
    return info


def set(cmd, target_id):
    """
    Select the default target to use when submitting jobs to Azure Quantum.
    """
    info = TargetInfo(cmd, target_id)
    if info:
        info.save(cmd)
    return info


def list(cmd, resource_group_name, workspace_name, location):
    """
    Get the list of providers and their targets in an Azure Quantum workspace.
    """
    info = WorkspaceInfo(cmd, resource_group_name, workspace_name, location)
    client = cf_providers(cmd.cli_ctx, info.subscription, info.resource_group, info.name, info.location)
    return client.get_status()


def clear(cmd):
    """
    Clear the default target-id.
    """
    info = TargetInfo(cmd)
    info.clear()
    info.save(cmd)


# Added to fix output problem
# def show(cmd, target_id):
def target_show(cmd, target_id):
    """
    Show the currently selected default target.
    """
    info = TargetInfo(cmd, target_id)
    info.target_id += ""    # Kludge excuse: Without this the only output we ever get is "targetId": {"isDefault": true}
    return info


def get_provider(cmd, target_id, resource_group_name, workspace_name, location):
    """
    Get the the Provider ID for a specific target
    """
    provider_id = None
    provider_list = list(cmd, resource_group_name, workspace_name, location)
    if provider_list is not None:
        for item in provider_list:
            for target_item in item.targets:
                if target_item.id.lower() == target_id.lower():
                    provider_id = item.id
                    break
            if provider_id is not None:
                break
    return provider_id
