# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long,redefined-builtin

from .._client_factory import cf_providers
from .workspace import WorkspaceInfo


class TargetInfo(object):
    def __init__(self, cmd, target_id=None):

        def select_value(key, value):
            if value is not None:
                return value
            value = cmd.cli_ctx.config.get('quantum', key, None)
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
            cmd.cli_ctx.config.set_value('quantum', 'target_id', self.target_id)


def show(cmd, target_id=None):
    """
    Get the details of the given (or current) target to use when submitting jobs to Azure Quantum.
    """
    info = TargetInfo(cmd, target_id)
    return info


def set(cmd, target_id=None):
    """
    Select the default target to use when submitting jobs to Azure Quantum.
    """
    info = TargetInfo(cmd, target_id)
    if info:
        info.save(cmd)
    return info


def list(cmd, resource_group_name=None, workspace_name=None, location=None):
    """
    Get the list of providers and their targets in an Azure Quantum workspace.
    """
    info = WorkspaceInfo(cmd, resource_group_name, workspace_name, location)
    client = cf_providers(cmd.cli_ctx, info.subscription, info.resource_group, info.name, info.location)
    return client.get_status()


def clear(cmd):
    """
    Unset the default target-id.
    """
    info = TargetInfo(cmd)
    info.clear()
    info.save(cmd)
