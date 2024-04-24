# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long,redefined-builtin,unnecessary-comprehension, too-many-locals, too-many-statements, too-many-nested-blocks

import os.path
import json
import sys
import time

from azure.cli.command_modules.storage.operations.account import list_storage_accounts

from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import DeploymentMode

from azure.cli.core.azclierror import (InvalidArgumentValueError, AzureInternalError,
                                       RequiredArgumentMissingError, ResourceNotFoundError)

from msrestazure.azure_exceptions import CloudError
from .._client_factory import cf_workspaces, cf_quotas, cf_workspace, cf_offerings, _get_data_credentials
from ..vendored_sdks.azure_mgmt_quantum.models import QuantumWorkspace
from ..vendored_sdks.azure_mgmt_quantum.models import QuantumWorkspaceIdentity
from ..vendored_sdks.azure_mgmt_quantum.models import Provider, APIKeys, WorkspaceResourceProperties
from ..vendored_sdks.azure_mgmt_quantum.models._enums import KeyType
from .offerings import accept_terms, _get_publisher_and_offer_from_provider_id, _get_terms_from_marketplace, OFFER_NOT_AVAILABLE, PUBLISHER_NOT_AVAILABLE

DEFAULT_WORKSPACE_LOCATION = 'westus'
DEFAULT_STORAGE_SKU = 'Standard_LRS'
DEFAULT_STORAGE_SKU_TIER = 'Standard'
DEFAULT_STORAGE_KIND = 'Storage'
SUPPORTED_STORAGE_SKU_TIERS = ['Standard']
SUPPORTED_STORAGE_KINDS = ['Storage', 'StorageV2']
DEPLOYMENT_NAME_PREFIX = 'Microsoft.AzureQuantum-'

POLLING_TIME_DURATION = 3  # Seconds
MAX_RETRIES_ROLE_ASSIGNMENT = 20
MAX_POLLS_CREATE_WORKSPACE = 300

C4A_TERMS_ACCEPTANCE_MESSAGE = "\nBy continuing you accept the Azure Quantum terms and conditions and privacy policy and agree that " \
                               "Microsoft can share your account details with the provider for their transactional purposes.\n\n" \
                               "https://privacy.microsoft.com/privacystatement\n" \
                               "https://azure.microsoft.com/support/legal/preview-supplemental-terms/\n\n" \
                               "Continue? (Y/N) "


class WorkspaceInfo:
    def __init__(self, cmd, resource_group_name=None, workspace_name=None, location=None):
        from azure.cli.core.commands.client_factory import get_subscription_id

        # Hierarchically selects the value for the given key.
        # First tries the value provided as argument, as that represents the value from the command line
        # then it checks if the key exists in the [defaults] section in config, and uses that if available.
        def select_value(key, value):
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

        # Save in the global [defaults] section of the .azure\config file
        with ConfiguredDefaultSetter(cmd.cli_ctx.config, False):
            cmd.cli_ctx.config.set_value(cmd.cli_ctx.config.defaults_section_name, 'group', self.resource_group)
            cmd.cli_ctx.config.set_value(cmd.cli_ctx.config.defaults_section_name, 'workspace', self.name)
            cmd.cli_ctx.config.set_value(cmd.cli_ctx.config.defaults_section_name, 'location', self.location)


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


def _autoadd_providers(cmd, providers_in_region, providers_selected, workspace_location, auto_accept):
    already_accepted_terms = False
    for provider in providers_in_region:
        for sku in provider.properties.skus:
            if sku.auto_add:
                # Don't duplicate a provider if it was also specified in the command's -r parameter
                provider_already_added = False
                for already_selected_provider in providers_selected:
                    if already_selected_provider['provider_id'] == provider.id:
                        provider_already_added = True
                        break
                if not provider_already_added:
                    (publisher, offer) = _get_publisher_and_offer_from_provider_id(providers_in_region, provider.id)
                    if (offer is None or publisher is None):
                        raise RequiredArgumentMissingError(f"Error adding 'autoAdd' provider: Publisher or Offer not found for '{provider.id}'")

                    provider_selected = {'provider_id': provider.id, 'sku': sku.id, 'offer_id': offer, 'publisher_id': publisher}
                    if cmd is not None and not already_accepted_terms and _provider_terms_need_acceptance(cmd, provider_selected):
                        if not auto_accept:
                            print(C4A_TERMS_ACCEPTANCE_MESSAGE, end='')
                            if input().lower() != 'y':
                                sys.exit('Terms not accepted. No workspace created.')
                        accept_terms(cmd, provider.id, sku.id, workspace_location)
                        already_accepted_terms = True
                    providers_selected.append(provider_selected)


def _add_quantum_providers(cmd, workspace, providers, auto_accept, skip_autoadd):
    providers_in_region_paged = cf_offerings(cmd.cli_ctx).list(location_name=workspace.location)
    providers_in_region = [item for item in providers_in_region_paged]
    providers_selected = []
    if providers is not None:
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
    if not skip_autoadd:
        _autoadd_providers(cmd, providers_in_region, providers_selected, workspace.location, auto_accept)

    # If there weren't any autoAdd providers and none were specified with the -r parameter, we have a problem...
    if not providers_selected:
        raise RequiredArgumentMissingError("A list of Azure Quantum providers and SKUs (plans) is required.",
                                           "Supply the missing -r parameter. For example:\n"
                                           "\t-r \"Microsoft/Basic, Microsoft.FleetManagement/Basic\"\n"
                                           "To display a list of Provider IDs and their SKUs, use the following command:\n"
                                           "\taz quantum offerings list -l MyLocation -o table")

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


def _validate_storage_account(tier_or_kind_msg_text, tier_or_kind, supported_tiers_or_kinds):
    if tier_or_kind not in supported_tiers_or_kinds:
        tier_or_kind_list = ', '.join(supported_tiers_or_kinds)
        plural = 's' if len(supported_tiers_or_kinds) != 1 else ''
        raise InvalidArgumentValueError(f"Storage account {tier_or_kind_msg_text} '{tier_or_kind}' is not supported.\n"
                                        f"Storage account {tier_or_kind_msg_text}{plural} currently supported: {tier_or_kind_list}")


def create(cmd, resource_group_name, workspace_name, location, storage_account, skip_role_assignment=False,
           provider_sku_list=None, auto_accept=False, skip_autoadd=False):
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
    info = WorkspaceInfo(cmd, resource_group_name, workspace_name, location)
    if not info.resource_group:
        raise ResourceNotFoundError("Please run 'az quantum workspace set' first to select a default resource group.")
    quantum_workspace = _get_basic_quantum_workspace(location, info, storage_account)

    # Until the "--skip-role-assignment" parameter is deprecated, use the old non-ARM code to create a workspace without doing a role assignment
    if skip_role_assignment:
        _add_quantum_providers(cmd, quantum_workspace, provider_sku_list, auto_accept, skip_autoadd)
        properties = WorkspaceResourceProperties()
        properties.providers = quantum_workspace.providers
        properties.api_key_enabled = True
        quantum_workspace.properties = properties
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

    _add_quantum_providers(cmd, quantum_workspace, provider_sku_list, auto_accept, skip_autoadd)
    validated_providers = []
    for provider in quantum_workspace.providers:
        validated_providers.append({"providerId": provider.provider_id, "providerSku": provider.provider_sku})

    # Set default storage account parameters in case the storage account does not exist yet
    storage_account_sku = DEFAULT_STORAGE_SKU
    storage_account_sku_tier = DEFAULT_STORAGE_SKU_TIER
    storage_account_kind = DEFAULT_STORAGE_KIND
    storage_account_location = location

    # Look for info on existing storage account
    storage_account_list = list_storage_accounts(cmd, resource_group_name)
    if storage_account_list:
        for storage_account_info in storage_account_list:
            if storage_account_info.name == storage_account:
                storage_account_sku = storage_account_info.sku.name
                storage_account_sku_tier = storage_account_info.sku.tier
                storage_account_kind = storage_account_info.kind
                storage_account_location = storage_account_info.location
                break

    # Validate the storage account SKU tier and kind
    _validate_storage_account('tier', storage_account_sku_tier, SUPPORTED_STORAGE_SKU_TIERS)
    _validate_storage_account('kind', storage_account_kind, SUPPORTED_STORAGE_KINDS)

    parameters = {
        'quantumWorkspaceName': workspace_name,
        'location': location,
        'tags': {},
        'providers': validated_providers,
        'storageAccountName': storage_account,
        'storageAccountId': _get_storage_account_path(info, storage_account),
        'storageAccountLocation': storage_account_location,
        'storageAccountSku': storage_account_sku,
        'storageAccountKind': storage_account_kind,
        'storageAccountDeploymentName': "Microsoft.StorageAccount-" + time.strftime("%d-%b-%Y-%H-%M-%S", time.gmtime())
    }
    parameters = {k: {'value': v} for k, v in parameters.items()}

    deployment_properties = {
        'mode': DeploymentMode.incremental,
        'template': template,
        'parameters': parameters
    }

    credentials = _get_data_credentials(cmd.cli_ctx, info.subscription)
    arm_client = ResourceManagementClient(credentials, info.subscription)

    # Show the first progress indicator dot before starting ARM template deployment
    print('.', end='', flush=True)

    deployment_async_operation = arm_client.deployments.begin_create_or_update(
        info.resource_group,
        (DEPLOYMENT_NAME_PREFIX + workspace_name)[:64],
        {'properties': deployment_properties}
    )

    # Show progress indicator dots
    polling_cycles = 0
    while not deployment_async_operation.done():
        polling_cycles += 1
        if polling_cycles > MAX_POLLS_CREATE_WORKSPACE:
            print()
            raise AzureInternalError("Create quantum workspace operation timed out.")

        print('.', end='', flush=True)
        time.sleep(POLLING_TIME_DURATION)
    print()
    quantum_workspace = deployment_async_operation.result()
    return quantum_workspace


def delete(cmd, resource_group_name, workspace_name):
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


def quotas(cmd, resource_group_name, workspace_name, location):
    """
    List the quotas for the given (or current) Azure Quantum workspace.
    """
    info = WorkspaceInfo(cmd, resource_group_name, workspace_name, location)
    client = cf_quotas(cmd.cli_ctx, info.subscription, info.resource_group, info.name, info.location)
    return client.list()


def set(cmd, workspace_name, resource_group_name, location):
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


def list_keys(cmd, resource_group_name=None, workspace_name=None):
    """
    List Azure Quantum workspace api keys.
    """
    client = cf_workspace(cmd.cli_ctx)
    info = WorkspaceInfo(cmd, resource_group_name, workspace_name, None)
    if (not info.resource_group) or (not info.name):
        raise ResourceNotFoundError("Please run 'az quantum workspace set' first to select a default Quantum Workspace.")

    keys = client.list_keys(resource_group_name=info.resource_group, workspace_name=info.name)
    return keys


def regenerate_keys(cmd, resource_group_name=None, workspace_name=None, key_type=None):
    """
    Regenerate Azure Quantum workspace api keys.
    """
    client = cf_workspace(cmd.cli_ctx)
    info = WorkspaceInfo(cmd, resource_group_name, workspace_name, None)
    if (not info.resource_group) or (not info.name):
        raise ResourceNotFoundError("Please run 'az quantum workspace set' first to select a default Quantum Workspace.")

    if not key_type:
        raise RequiredArgumentMissingError("Please select the api key to regenerate.")

    keys = []
    if key_type is not None:
        for key in key_type.split(','):
            keys.append(KeyType[key])

    key_specification = APIKeys(keys=keys)
    response = client.regenerate_keys(resource_group_name=info.resource_group, workspace_name=info.name, key_specification=key_specification)
    return response


def enable_keys(cmd, resource_group_name=None, workspace_name=None, enable_key=None):
    """
    Update the default Azure Quantum workspace.
    """
    client = cf_workspaces(cmd.cli_ctx)
    info = WorkspaceInfo(cmd, resource_group_name, workspace_name, None)
    if (not info.resource_group) or (not info.name):
        raise ResourceNotFoundError("Please run 'az quantum workspace set' first to select a default Quantum Workspace.")

    if enable_key not in ["True", "true", "False", "false"]:
        raise InvalidArgumentValueError("Please set –-enable-api-key to be True/true or False/false.")

    ws = client.get(info.resource_group, info.name)

    if (enable_key in ["True", "true"]):
        ws.properties.api_key_enabled = True
    elif (enable_key in ["False", "false"]):
        ws.properties.api_key_enabled = False
    ws = client.begin_create_or_update(info.resource_group, info.name, ws)
    if ws:
        info.save(cmd)
    return ws
