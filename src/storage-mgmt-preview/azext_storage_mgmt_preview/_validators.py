# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._client_factory import storage_client_factory


def _query_account_rg(cli_ctx, account_name):
    """Query the storage account's resource group, which the mgmt sdk requires."""
    scf = storage_client_factory(cli_ctx)
    acc = next((x for x in scf.storage_accounts.list() if x.name == account_name), None)
    if acc:
        from msrestazure.tools import parse_resource_id
        return parse_resource_id(acc.id)['resource_group'], scf
    raise ValueError("Storage account '{}' not found.".format(account_name))


def process_resource_group(cmd, namespace):
    """Processes the resource group parameter from the account name"""
    if namespace.account_name and not namespace.resource_group_name:
        namespace.resource_group_name = _query_account_rg(cmd.cli_ctx, namespace.account_name)[0]


def validate_delete_retention_days(namespace):
    if namespace.enable_delete_retention is True and namespace.delete_retention_days is None:
        raise ValueError(
            "incorrect usage: you have to provide value for '--delete-retention-days' when '--enable-delete-retention' "
            "is set to true")

    if namespace.enable_delete_retention is False and namespace.delete_retention_days is not None:
        raise ValueError(
            "incorrect usage: '--delete-retention-days' is invalid when '--enable-delete-retention' is set to false")
