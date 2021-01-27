# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long,redefined-builtin

from knack.util import CLIError

from .._client_factory import cf_workspaces
from ..vendored_sdks.azure_mgmt_quantum.models import QuantumWorkspace
from ..vendored_sdks.azure_mgmt_quantum.models import QuantumWorkspaceIdentity
from ..vendored_sdks.azure_mgmt_quantum.models import Provider
from msrestazure.azure_exceptions import CloudError

import time

DEFAULT_WORKSPACE_LOCATION = 'westus'
POLLING_TIME_DURATION = 3
MAX_RETRIES_ROLE_ASSIGNMENT = 10

class WorkspaceInfo(object):
    def __init__(self, cmd, resource_group_name=None, workspace_name=None, location=None):
        from azure.cli.core.commands.client_factory import get_subscription_id

        # Hierarchically selects the value for the given key.
        # First tries the value provided as argument, as that represents the value from the command line
        # then it checks if the key exists in the 'quantum' section in config, and uses that if available.
        # finally, it checks in the 'global' section in the config.
        def select_value(key, value):
            if value is not None:
                return value
            value = cmd.cli_ctx.config.get('quantum', key, None)
            if value is not None:
                return value
            value = cmd.cli_ctx.config.get(cmd.cli_ctx.config.defaults_section_name, key, None)
            return value

        self.subscription = get_subscription_id(cmd.cli_ctx)
        self.resource_group = select_value('group', resource_group_name)
        self.name = select_value('workspace', workspace_name)
        self.location = select_value('location', location)

    def clear(self):
        self.subscription = ''
        self.resource_group = ''
        self.name = ''
        self.location = ''

    def save(self, cmd):
        from azure.cli.core.util import ConfiguredDefaultSetter

        with ConfiguredDefaultSetter(cmd.cli_ctx.config, False):
            cmd.cli_ctx.config.set_value('quantum', 'group', self.resource_group)
            cmd.cli_ctx.config.set_value('quantum', 'workspace', self.name)
            cmd.cli_ctx.config.set_value('quantum', 'location', self.location)


def _show_tip(msg):
    import colorama
    colorama.init()
    print(f"\033[1m{colorama.Fore.YELLOW}{msg}{colorama.Style.RESET_ALL}")


def _get_storage_account_path(workspaceInfo, storage_account_name):
    if (storage_account_name[0] == "/"):
        path = storage_account_name
    else:
        path = f"/subscriptions/{workspaceInfo.subscription}/resourceGroups/{workspaceInfo.resource_group}/providers/Microsoft.Storage/storageAccounts/{storage_account_name}"
    return path


def _get_basic_quantum_workspace(location, info, storage_account):
    qw = QuantumWorkspace(location=location)
    # Use a default provider 
    # Replace this with user specified providers as part of task 16184.
    prov = Provider()
    prov.provider_id = "Microsoft"
    prov.provider_sku = "Basic"
    qw.providers = [prov]
    # Allow the system to assign the workspace identity
    qw.identity = QuantumWorkspaceIdentity()
    qw.identity.type = "SystemAssigned"
    qw.storage_account = _get_storage_account_path(info, storage_account)
    return qw


def _create_role_assignment(cmd, quantum_workspace):
    from azure.cli.command_modules.role.custom import create_role_assignment
    retry_attempts = 0
    while (retry_attempts < MAX_RETRIES_ROLE_ASSIGNMENT):
        try:
            create_role_assignment(cmd, role="Contributor", scope=quantum_workspace.storage_account, assignee=quantum_workspace.identity.principal_id)
            break
        except (CloudError, CLIError) as e:
            error = str(e.args).lower()
            if (("does not exist" in error) or ("cannot find" in error)):
                print('.', end='', flush=True)
                time.sleep(POLLING_TIME_DURATION)
                retry_attempts += 1
                continue
            raise e
        except Exception as x:
            raise CLIError(f"Role assignment encountered exception ({type(x).__name__}): {x}")
    if (retry_attempts > 0):
        print("") # To end the line of the waiting indicators.
    if (retry_attempts == MAX_RETRIES_ROLE_ASSIGNMENT):
        raise CLIError(f"Role assignment could not be added to storage account {quantum_workspace.storage_account}.")
    return quantum_workspace


def create(cmd, resource_group_name=None, workspace_name=None, location=None, storage_account=None):
    """
    Create a new Azure Quantum workspace.
    """
    client = cf_workspaces(cmd.cli_ctx)
    if (not workspace_name):
        raise CLIError("An explicit workspace name is required for this command.")
    if (not storage_account):
        raise CLIError("A quantum workspace requires a valid storage account.")
    if (not location):
        raise CLIError("A location for the new quantum workspace is required.")
    info = WorkspaceInfo(cmd, resource_group_name, workspace_name, location)
    if (not info.resource_group):
        raise CLIError("Please run 'az quantum workspace set' first to select a default resource group.")
    _show_tip(f"Workspace {info.name} will be created with the Basic SKU of the Microsoft QIO optimization provider.")
    _show_tip("Please go to the Azure portal https://portal.azure.com/ to configure additional providers.")
    quantum_workspace = _get_basic_quantum_workspace(location, info, storage_account)
    poller = client.create_or_update(info.resource_group, info.name, quantum_workspace, polling=False)
    while not poller.done():
        time.sleep(POLLING_TIME_DURATION)
    quantum_workspace = poller.result()
    return _create_role_assignment(cmd, quantum_workspace)


def delete(cmd, resource_group_name=None, workspace_name=None):
    """
    Delete the given (or current) Azure Quantum workspace.
    """
    client = cf_workspaces(cmd.cli_ctx)
    info = WorkspaceInfo(cmd, resource_group_name, workspace_name)
    if (not info.resource_group) or (not info.name):
        raise CLIError("Please run 'az quantum workspace set' first to select a default Quantum Workspace.")
    client.delete(info.resource_group, info.name, polling=False)
    # If we deleted the current workspace, clear it
    curr_ws = WorkspaceInfo(cmd)
    if (curr_ws.resource_group == info.resource_group and curr_ws.name == info.name):
        curr_ws.clear()
        curr_ws.save(cmd)
    # Get updated information from the affected workspace
    ws = client.get(info.resource_group, info.name)
    return ws

def list(cmd, resource_group_name=None, tag=None, location=None):
    """
    Get the list of Azure Quantum workspaces available.
    """
    from azure.cli.command_modules.resource.custom import list_resources
    return list_resources(cmd, resource_group_name=resource_group_name, resource_type="Microsoft.Quantum/Workspaces", tag=tag, location=location)


def show(cmd, resource_group_name=None, workspace_name=None):
    """
    Get the details of the given (or current) Azure Quantum workspace.
    """
    client = cf_workspaces(cmd.cli_ctx)
    info = WorkspaceInfo(cmd, resource_group_name, workspace_name, None)
    if (not info.resource_group) or (not info.name):
        raise CLIError("Please run 'az quantum workspace set' first to select a default Quantum Workspace.")
    ws = client.get(info.resource_group, info.name)
    return ws


def set(cmd, workspace_name, resource_group_name=None, location=None):
    """
    Set the default Azure Quantum workspace.
    """
    client = cf_workspaces(cmd.cli_ctx)
    info = WorkspaceInfo(cmd, resource_group_name, workspace_name, location)
    ws = client.get(info.resource_group, info.name)
    if ws:
        info.save(cmd)
    return ws


def clear(cmd):
    """
    Clear the default Azure Quantum workspace.
    """
    info = WorkspaceInfo(cmd)
    info.clear()
    info.save(cmd)
