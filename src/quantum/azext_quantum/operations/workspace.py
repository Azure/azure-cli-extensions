# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=import-outside-toplevel,line-too-long,redefined-builtin

from knack.util import CLIError

from .._client_factory import cf_workspaces

class WorkspaceInfo(object):
    def __init__(self, cmd, resource_group_name=None, workspace_name=None):
        from azure.cli.core.commands.client_factory import get_subscription_id

        # Hierarchically selects the value for the given key.
        # First tries the value provided as argument, as that represents the value from the command line
        # then it checks if the key exists in the 'quantum' section in config, and uses that if available.
        # finally, it checks in the 'global' section in the config.
        def select_value(key, value):
            if not value is None:
                return value
            value = cmd.cli_ctx.config.get('quantum', key, None)
            if not value is None:
                return value
            value = cmd.cli_ctx.config.get(cmd.cli_ctx.config.defaults_section_name, key, None)
            if not value is None:
                return value

        self.subscription = get_subscription_id(cmd.cli_ctx)
        self.resource_group = select_value('group', resource_group_name)
        self.name = select_value('workspace', workspace_name)

    def clear(self):
        self.subscription = ''
        self.resource_group = ''
        self.name = ''

    def save(self, cmd):
        from azure.cli.core.util import ConfiguredDefaultSetter

        with ConfiguredDefaultSetter(cmd.cli_ctx.config, False):
            cmd.cli_ctx.config.set_value('quantum', 'group', self.resource_group)
            cmd.cli_ctx.config.set_value('quantum', 'workspace', self.name)


def list(cmd, resource_group_name=None, tag=None, location=None):
    """
    Returns the list of Quantum Workspaces available.
    """
    from azure.cli.command_modules.resource.custom import list_resources
    return list_resources(cmd, resource_group_name=resource_group_name, resource_type="Microsoft.Quantum/Workspaces", tag=tag, location=location)

def show(cmd, resource_group_name=None, workspace_name=None):
    """
    Returns the details of the given (or current) Quantum Workspace.
    """
    client = cf_workspaces(cmd.cli_ctx)
    info = WorkspaceInfo(cmd, resource_group_name, workspace_name)
    if (not info.resource_group) or (not info.name):
        raise CLIError("Please run 'az quantum workspace set' first to select a default Quantum Workspace.")
    ws = client.get(info.resource_group, info.name)
    return ws

def set(cmd, workspace_name, resource_group_name=None):
    """
    Sets the default Quantum Workspace.
    """
    client = cf_workspaces(cmd.cli_ctx)
    info = WorkspaceInfo(cmd, resource_group_name, workspace_name)
    ws = client.get(info.resource_group, info.name)
    if ws:
        info.save(cmd)
        return ws

def clear(cmd):
    """
    Unsets the default Quantum Workspace.
    """
    info = WorkspaceInfo(cmd)
    info.clear()
    info.save(cmd)
