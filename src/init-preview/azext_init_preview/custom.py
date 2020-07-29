# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import sys
import subprocess
from .pyaz import az
from knack.log import get_logger
from knack.prompting import prompt, prompt_y_n, prompt_choice_list
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import ResourceType
from azure.cli.command_modules.storage._validators import _query_account_rg
from azure.cli.core.commands.parameters import get_subscription_locations

logger = get_logger(__name__)


def create_storage_account(cmd, storage_account):
    resource_group = prompt(msg="[unicode] Please specify resource group name to host storage account: ")
    #resource_group = 'zuhtest'
    resource_client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES).resource_groups
    if resource_client.check_existence(resource_group_name=resource_group):
        logger.warning("Existing resource group '{}' is used. ".format(resource_group))
    else:
        location_list = az('account list-locations --query [].name').out.strip('[]\n').split(',\n ')
        choice = prompt_choice_list(msg="Please specify the location for your resource group: ", a_list=location_list,
                                    default=1)
        location = location_list[choice].strip(' "')
        logger.warning("Create resource group '{}' in location '{}'.".format(resource_group, location))
        #resource_client.create_or_update(resource_group_name=resource_group, parameters={'location': location})

    # Create storage account
    storage_client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_STORAGE).storage_accounts
    t_kind, t_sku_name = cmd.get_models('Kind', 'SkuName', resource_type=ResourceType.MGMT_STORAGE)
    kind = prompt_choice_list(msg="Please specify kind for your storage account: ", a_list=t_kind)
    sku = prompt_choice_list(msg="Please specify kind for your storage account: ", a_list=t_sku_name)


    #storage_client.create(resource_group_name=resource_group, account_name=storage_account, paramsters=storage_account_parameters)

    return resource_group


def check_storage_account(cmd):

    #storage_account = prompt(msg="Please specify the storage account name to create or existing storage account name: ")
    storage_account ='tckftakf'
    storage_client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_STORAGE).storage_accounts
    try:
        resource_group, _ = _query_account_rg(cmd.cli_ctx, storage_account)
        properties = storage_client.get_properties(account_name=storage_account, resource_group_name=resource_group)
        ans = prompt("""
Do you want use existing storage account '{}' in resource group '{}' with the following properties: \n
- Kind: {} \n
- Sku: {} \n
- Hierarchical namespace (ADLS Gen2): {} \n
- Location: {} \n
If yes, input 'y'. If not, enter 'n' to input new storage account name or enter 'q' to quit: 
""".format(storage_account, resource_group, properties.kind, properties.sku.name,
           True if properties.is_hns_enabled else False, properties.location))
        return storage_account, ans
    except ValueError:
        ans = create_storage_account(cmd, storage_account)
        return storage_account, ans


def storage_init(cmd):

    # Start creating storage account
    logger.warning("To init with storage module, we will start from creating storage account.")

    # Check existence of storage account
    storage_account, ans = check_storage_account(cmd)
    while ans is 'n':
        storage_account, ans = check_storage_account(cmd)
        if ans.lower() in ["q", "quit"]:
            break

    # Check existence of storage account



