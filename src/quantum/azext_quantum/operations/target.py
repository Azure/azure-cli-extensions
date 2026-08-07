# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long,redefined-builtin,unused-argument

from azure.cli.core.azclierror import InvalidArgumentValueError
from .._client_factory import cf_providers, cf_suite_offers, cf_provider_account_status
from .._list_helper import repack_response_json
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


def list(cmd, resource_group_name=None, workspace_name=None, provider_id=None, location=None):
    """
    Get the list of providers and their targets in an Azure Quantum workspace, or in a
    provider account when --provider-id is specified.
    """
    if provider_id:
        return _list_by_provider_account(cmd, provider_id, location)

    info = WorkspaceInfo(cmd, resource_group_name, workspace_name)
    client = cf_providers(cmd.cli_ctx, info.subscription, info.resource_group, info.name, info.endpoint)
    response = client.list(info.subscription, info.resource_group, info.name)
    return repack_response_json(response)


def _get_provider_account_location(cmd, provider_id):
    """
    Resolve the region for a provider account (suite offer) from its subscription-level listing.
    """
    for offer in cf_suite_offers(cmd.cli_ctx).list_by_subscription():
        if offer.properties.provider_id.lower() == provider_id.lower():
            return offer.properties.location
    raise InvalidArgumentValueError(f"Provider account '{provider_id}' not found in the current subscription.")


def _list_by_provider_account(cmd, provider_id, location):
    """
    Get the list of targets and their status for a provider account (suite offer).
    """
    from azure.cli.core.commands.client_factory import get_subscription_id

    subscription = get_subscription_id(cmd.cli_ctx)
    if not location:
        location = _get_provider_account_location(cmd, provider_id)

    status = cf_provider_account_status(cmd.cli_ctx, subscription, location, provider_id)

    # Provider accounts that failed provisioning are omitted by the data-plane listing, so no
    # additional filtering is required here. Normalize the response into a list of providers.
    if isinstance(status, dict):
        providers = status.get('value', [status])
    else:
        providers = status
    return providers


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


def get_provider(cmd, target_id, resource_group_name, workspace_name):
    """
    Get the the Provider ID for a specific target
    """
    provider_id = None
    provider_list = list(cmd, resource_group_name, workspace_name)
    if provider_list is not None:
        for item in provider_list:
            for target_item in item["targets"]:
                if target_item["id"].lower() == target_id.lower():
                    provider_id = item["id"]
                    break
            if provider_id is not None:
                break
    return provider_id
