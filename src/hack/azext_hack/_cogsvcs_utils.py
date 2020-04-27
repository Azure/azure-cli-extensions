# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from azure.cli.command_modules.cognitiveservices._client_factory import cf_accounts
from azure.cli.command_modules.cognitiveservices.custom import create


def get_cogsvcs_key(cmd, name):
    cogsvcs_client = get_mgmt_service_client(
        cmd.cli_ctx, CognitiveServicesManagementClient)
    return cogsvcs_client.accounts.list_keys(name, name).key1


def create_cogsvcs_key(cmd, name, location):
    client = cf_accounts(cmd.cli_ctx)
    return create(client, resource_group_name=name,
                  account_name=name, sku_name='S0',
                  kind='CognitiveServices', location=location)
