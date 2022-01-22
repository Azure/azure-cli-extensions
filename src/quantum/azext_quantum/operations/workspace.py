# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long,redefined-builtin,unnecessary-comprehension

import os.path
import json
import time

from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import DeploymentMode

from azure.cli.core.azclierror import (InvalidArgumentValueError, AzureInternalError,
                                       RequiredArgumentMissingError, ResourceNotFoundError)

from msrestazure.azure_exceptions import CloudError
from .._client_factory import cf_workspaces, cf_quotas, cf_offerings, _get_data_credentials
from ..vendored_sdks.azure_mgmt_quantum.models import QuantumWorkspace
from ..vendored_sdks.azure_mgmt_quantum.models import QuantumWorkspaceIdentity
from ..vendored_sdks.azure_mgmt_quantum.models import Provider
from .offerings import _get_publisher_and_offer_from_provider_id, _get_terms_from_marketplace, OFFER_NOT_AVAILABLE, PUBLISHER_NOT_AVAILABLE

DEFAULT_WORKSPACE_LOCATION = 'westus'
POLLING_TIME_DURATION = 3  # Seconds
MAX_RETRIES_ROLE_ASSIGNMENT = 20


class WorkspaceInfo:
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
    if storage_account_name[0] == "/":
        path = storage_account_name
    else:
        path = f"/subscriptions/{workspaceInfo.subscription}/resourceGroups/{workspaceInfo.resource_group}/providers/Microsoft.Storage/storageAccounts/{storage_account_name}"
    return path


def _get_basic_quantum_workspace(location, info, storage_account):
    qw = QuantumWorkspace(location=location)
    qw.providers = []
    # Allow the system to assign the workspace identity
    qw.identity = QuantumWorkspaceIdentity()
    qw.identity.type = "SystemAssigned"
    qw.storage_account = _get_storage_account_path(info, storage_account)
    return qw


def _provider_terms_need_acceptance(cmd, provider):
    if (provider['offer_id'] == OFFER_NOT_AVAILABLE or provider['publisher_id'] == PUBLISHER_NOT_AVAILABLE):
        # No need to accept terms
        return False

    return not _get_terms_from_marketplace(cmd, provider['publisher_id'], provider['offer_id'], provider['sku']).accepted


def _add_quantum_providers(cmd, workspace, providers):
    providers_in_region_paged = cf_offerings(cmd.cli_ctx).list(location_name=workspace.location)
    providers_in_region = [item for item in providers_in_region_paged]
    providers_selected = []
    for pair in providers.split(','):
        es = [e.strip() for e in pair.split('/')]
        if len(es) != 2:
            raise InvalidArgumentValueError(f"Invalid Provider/SKU specified: '{pair.strip()}'")
        provider_id = es[0]
        sku = es[1]
        (publisher, offer) = _get_publisher_and_offer_from_provider_id(providers_in_region, provider_id)
        if (offer is None or publisher is None):
            raise InvalidArgumentValueError(f"Provider '{provider_id}' not found in region {workspace.location}.")
        providers_selected.append({'provider_id': provider_id, 'sku': sku, 'offer_id': offer, 'publisher_id': publisher})
    _show_tip(f"Workspace creation has been requested with the following providers:\n{providers_selected}")
    # Now that the providers have been requested, add each of them into the workspace
    for provider in providers_selected:
        if _provider_terms_need_acceptance(cmd, provider):
            raise InvalidArgumentValueError(f"Terms for Provider '{provider['provider_id']}' and SKU '{provider['sku']}' have not been accepted.\n"
                                            "Use command 'az quantum offerings accept-terms' to accept them.")
        p = Provider()
        p.provider_id = provider['provider_id']
        p.provider_sku = provider['sku']
        workspace.providers.append(p)


def _create_role_assignment(cmd, quantum_workspace):
    from azure.cli.command_modules.role.custom import create_role_assignment
    retry_attempts = 0
    while retry_attempts < MAX_RETRIES_ROLE_ASSIGNMENT:
        try:
            create_role_assignment(cmd, role="Contributor", scope=quantum_workspace.storage_account, assignee=quantum_workspace.identity.principal_id)
            break
        except (CloudError, AzureInternalError) as e:
            error = str(e.args).lower()
            if (("does not exist" in error) or ("cannot find" in error)):
                print('.', end='', flush=True)
                time.sleep(POLLING_TIME_DURATION)
                retry_attempts += 1
                continue
            raise e
        except Exception as x:
            raise AzureInternalError(f"Role assignment encountered exception ({type(x).__name__}): {x}") from x
    if retry_attempts > 0:
        print()  # To end the line of the waiting indicators.
    if retry_attempts == MAX_RETRIES_ROLE_ASSIGNMENT:
        max_time_in_seconds = MAX_RETRIES_ROLE_ASSIGNMENT * POLLING_TIME_DURATION
        raise AzureInternalError(f"Role assignment could not be added to storage account {quantum_workspace.storage_account} within {max_time_in_seconds} seconds.")
    return quantum_workspace


def create(cmd, resource_group_name=None, workspace_name=None, location=None, storage_account=None, skip_role_assignment=False, provider_sku_list=None):
    """
    Create a new Azure Quantum workspace.
    """
    client = cf_workspaces(cmd.cli_ctx)
    if not workspace_name:
        raise RequiredArgumentMissingError("An explicit workspace name is required for this command.")
    if not storage_account:
        raise RequiredArgumentMissingError("A quantum workspace requires a valid storage account.")
    if not location:
        raise RequiredArgumentMissingError("A location for the new quantum workspace is required.")
    if provider_sku_list is None:
        raise RequiredArgumentMissingError("A list of Azure Quantum providers and SKUs is required.")
    info = WorkspaceInfo(cmd, resource_group_name, workspace_name, location)
    if not info.resource_group:
        raise ResourceNotFoundError("Please run 'az quantum workspace set' first to select a default resource group.")
    quantum_workspace = _get_basic_quantum_workspace(location, info, storage_account)

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Old code...
    # _add_quantum_providers(cmd, quantum_workspace, provider_sku_list)
    # poller = client.begin_create_or_update(info.resource_group, info.name, quantum_workspace, polling=False)
    # while not poller.done():
    #     time.sleep(POLLING_TIME_DURATION)
    # quantum_workspace = poller.result()
    # if not skip_role_assignment:
    #     quantum_workspace = _create_role_assignment(cmd, quantum_workspace)
    # return quantum_workspace
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    # Until the skip_role_assignment flag is deprecated, envoke the old code to create a workspace without doing a role assignment
    if skip_role_assignment:
        _add_quantum_providers(cmd, quantum_workspace, provider_sku_list)
        poller = client.begin_create_or_update(info.resource_group, info.name, quantum_workspace, polling=False)
        while not poller.done():
            time.sleep(POLLING_TIME_DURATION)
        quantum_workspace = poller.result()
        return quantum_workspace

    # ARM-template-based code to create an Azure Quantum workspace and make it a "Contributor" to the storage account
    template_path = os.path.join(os.path.dirname(
        __file__), 'templates', 'create-workspace-and-assign-role.json')
    with open(template_path, 'r', encoding='utf8') as template_file_fd:
        template = json.load(template_file_fd)

    _add_quantum_providers(cmd, quantum_workspace, provider_sku_list)
    validated_providers = []
    for provider in quantum_workspace.providers:
        validated_providers.append({"providerId": provider.provider_id, "providerSku": provider.provider_sku})

    parameters = {
        'quantumWorkspaceName': workspace_name,
        'location': location,
        'tags': {},
        'providers': validated_providers,
        'storageAccountName': storage_account,
        'storageAccountId': _get_storage_account_path(info, storage_account),
        'storageAccountLocation': location,
        'storageAccountDeploymentName': "Microsoft.StorageAccount-" + time.strftime("%d-%b-%Y-%H-%M-%S", time.gmtime())
    }
    parameters = {k: {'value': v} for k, v in parameters.items()}

    deployment_properties = {
        'mode': DeploymentMode.incremental,
        'template': template,
        'parameters': parameters
    }

    # >>>>> Replacing the following code with _get_data_credentials()
    # >>>>> Delete after testing is complete
    # from os import getenv
    # client_id = getenv('AZURE_CLIENT_ID')
    # if client_id:
    #     from azure.identity import ClientSecretCredential
    #     credentials = ClientSecretCredential(               # Use service principal creds during automated execution
    #         tenant_id=getenv('AZURE_TENANT_ID'),
    #         client_id=client_id,
    #         client_secret=getenv('AZURE_CLIENT_SECRET')
    #     )
    # else:
    #     from azure.identity import AzureCliCredential
    #     credentials = AzureCliCredential()                  # Requires user to have previously logged in with "az login"
    credentials = _get_data_credentials(cmd.cli_ctx, info.subscription)

    arm_client = ResourceManagementClient(credentials, info.subscription)

    deployment_async_operation = arm_client.deployments.begin_create_or_update(
        info.resource_group,
        # >>>>>"Microsoft.Quantum-" + time.strftime("%d-%b-%Y-%H-%M-%S", time.gmtime()),
        workspace_name,     # testsdk uses workspace name for deployment name in assert query
        {'properties': deployment_properties}
    )

    # Show progress indicator dots
    while not deployment_async_operation.done():
        print('.', end='', flush=True)
        time.sleep(POLLING_TIME_DURATION)
    print()
    quantum_workspace = deployment_async_operation.result()
    return quantum_workspace


def delete(cmd, resource_group_name=None, workspace_name=None):
    """
    Delete the given (or current) Azure Quantum workspace.
    """
    client = cf_workspaces(cmd.cli_ctx)
    info = WorkspaceInfo(cmd, resource_group_name, workspace_name)
    if (not info.resource_group) or (not info.name):
        raise ResourceNotFoundError("Please run 'az quantum workspace set' first to select a default Quantum Workspace.")
    client.begin_delete(info.resource_group, info.name, polling=False)
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


def get(cmd, resource_group_name=None, workspace_name=None):
    """
    Get the details of the given (or current) Azure Quantum workspace.
    """
    client = cf_workspaces(cmd.cli_ctx)
    info = WorkspaceInfo(cmd, resource_group_name, workspace_name, None)
    if (not info.resource_group) or (not info.name):
        raise ResourceNotFoundError("Please run 'az quantum workspace set' first to select a default Quantum Workspace.")
    ws = client.get(info.resource_group, info.name)
    return ws


def quotas(cmd, resource_group_name=None, workspace_name=None, location=None):
    """
    List the quotas for the given (or current) Azure Quantum workspace.
    """
    info = WorkspaceInfo(cmd, resource_group_name, workspace_name, location)
    client = cf_quotas(cmd.cli_ctx, info.subscription, info.resource_group, info.name, info.location)
    return client.list()


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
