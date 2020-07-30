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

t_kind = [
    {'name': 'StorageV2',
     'desc': 'Basic storage account type for blobs, Data Lake Gen2, files, queues, and tables. Recommended '
     'for most scenarios using Azure Storage, especially required for ADLS Gen2 account.'},
    {'name': 'FileStorage',
     'desc': 'Files-only storage accounts with premium performance characteristics. Recommended for enterprise or high '
     'performance scale applications.'},
    {'name': 'BlockBlobStorage',
     'desc': 'Storage accounts with premium performance characteristics for block blobs and append blobs. Recommended '
     'for scenarios with high transactions rates, or scenarios that use smaller objects or require consistently low '
     'storage latency.'},
    {'name': 'Storage',
     'desc': 'Legacy account type for blobs, files, queues, and tables. Use StorageV2 accounts instead when possible.'},
    {'name': 'BlobStorage',
     'desc': 'Legacy Blob-only storage accounts. Use StorageV2 accounts instead when possible.'},
    ]

t_performance = [
    {'name': 'Standard',
     'desc': 'For storing blobs, files, tables, queues, and Azure virtual machine disks. See more in '
             'https://docs.microsoft.com/en-us/azure/storage/common/scalability-targets-standard-account.'},
    {'name': 'Premium',
     'desc': 'For storing unmanaged virtual machine disks. See more in '
             'https://docs.microsoft.com/en-us/azure/storage/blobs/scalability-targets-premium-page-blobs.'}]

t_replication = [
    {'name': 'Locally redundant storage (LRS)',
     'desc': 'Replicate your data synchronously three times within a single physical location in the primary region. '
     'LRS is the least expensive replication option, but is not recommended for applications requiring high '
     'availability.'},
    {'name': 'Zone-redundant storage (ZRS)',
     'desc': 'Replicate your data synchronously across three Azure availability zones in the primary region. '
     'For applications requiring high availability, Microsoft recommends using ZRS in the primary region, and '
     'also replicating to a secondary region.'},
    {'name': 'Geo-redundant storage (GRS)',
     'desc': 'Replicate your data synchronously three times within a single physical location in the primary '
     'region using LRS. It then copies your data asynchronously to a single physical location in the secondary region.'},
    {'name': 'Geo-zone-redundant storage (GZRS)',
     'desc': 'Replicate your data synchronously across three Azure availability zones in the primary region '
     'using ZRS. It then copies your data asynchronously to a single physical location in the secondary region.'},
    {'name': 'Read-access geo-redundant storage (RA-GRS)',
     'desc': 'Same replication method as GRS, but enable read access to the secondary region, which will make sure'
     'your data is available to be read at all times, including in a situation where the primary region becomes '
     'unavailable.'},
    {'name': 'Read-access geo-zone-redundant storage (RA-GZRS)',
     'desc': 'Same replication method as GZRS, but enable read access to the secondary region, which will make sure'
     'your data is available to be read at all times, including in a situation where the primary region becomes '
     'unavailable.'}]

t_access_tier = [
    {'name': 'Hot',
     'desc': 'Optimized for storing data that is accessed frequently.'},
    {'name': 'Cool',
     'desc': 'Optimized for storing data that is infrequently accessed and stored for at least 30 days.'}]


def get_location(default_location=None):
    location_list = az('account list-locations --query [].name').out.strip('[]\n').split(',\n ')
    recommend = []
    if default_location:
        recommend.append(default_location)
    i = 1
    for location in location_list:
        recommend.append(location.strip(' "'))
        i += 1
        if i == 20:
            break
    return recommend


def get_performance(kind=None):
    result = []
    if kind in ['StorageV2', 'Storage', 'BlobStorage']:
        result.append(t_performance[0])
    if kind in ['StorageV2', 'Storage', 'BlockBlobStorage', 'FileStorage']:
        result.append(t_performance[1])
    return result


def get_replication(kind, performance):
    result = []
    if kind in ['StorageV2', 'Storage', 'BlobStorage', 'BlockBlobStorage', 'FileStorage']:  # LRS
        result.append(t_replication[0])
    if kind in ['StorageV2', 'BlockBlobStorage', 'FileStorage']:  # ZRS
        result.append(t_replication[1])
    if kind in ['StorageV2', 'Storage', 'BlobStorage']:  # GRS
        result.append(t_replication[2])
        result.append(t_replication[4])
    if kind in ['StorageV2']:  # GRS
        result.append(t_replication[3])
        result.append(t_replication[5])
    return result


def create_storage_account(cmd, storage_account):
    #resource_group = prompt(msg="Please specify resource group name to host storage account: ", level='Question')
    resource_group = 'zuh'
    resource_client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES).resource_groups
    if resource_client.check_existence(resource_group_name=resource_group):
        logger.warning("Existing resource group '{}' is used. ".format(resource_group))
        rg_location = resource_client.get(resource_group).location
    else:
        rg_location = prompt_choice_list(msg="Please specify the location for your resource group: ",
                                         a_list=get_location(), default=1)
        logger.warning("Create resource group '{}' in location '{}'.".format(resource_group, rg_location))
        #resource_client.create_or_update(resource_group_name=resource_group, parameters={'location': rg_location})

    # Create storage account
    location_list = get_location(rg_location)
    ans = prompt_choice_list(msg="Please specify the location of your storage account: ",
                             a_list=location_list, default=1,
                             level='Question')
    location = location_list[ans]

    ans = prompt_choice_list(
        msg="Please specify the type of your storage account. Each type supports different "
        "features and has its own pricing model. For more information, please see "
        "https://docs.microsoft.com/en-us/azure/storage/common/storage-account-overview#types-of-storage-accounts. "
        "The types of storage accounts are: ", a_list=t_kind, default=1, level="Question")
    kind = t_kind[ans]['name']

    performace_list = get_performance(kind)
    ans = prompt_choice_list(
        msg="Depending on the type of storage account you create, you can choose performance tiers: ",
        a_list=performace_list, default=1, level="Question")
    performance = performace_list[ans]['name']

    replication_list = get_replication(kind, performance)
    ans = prompt_choice_list(
        msg="Please choose a replication strategy that matches your durability requirements: ",
        a_list=replication_list, default=1, level="Question")
    replication = replication_list[ans]['name']
    import re
    p1 = re.compile(r'[(](.*?)[)]', re.S)
    replication = re.findall(p1, replication)[0]
    sku = '_'.join([performance, replication])
    cmd = 'storage account create -n {} -g {} -l {} --kind {} --sku {} '.format(
        storage_account, resource_group, location, kind, sku)

    if kind in ['StorageV2', 'BlobStorage']:
        ans = prompt_choice_list(
            msg="Please choose access tier used for billing your storage account: ",
            a_list=t_access_tier, default=1, level="Question")
        cmd = cmd + '--access-tier ' + t_access_tier[ans]['name']

    if kind == 'StorageV2':
        ans = prompt_y_n(msg="Do you want to create ADLS Gen2 account? ", level='Question')
        cmd = cmd + ' --hns ' + str(ans)

    print("Running the following CLI command to create specified storage account: \n"
                "{} \n".format(cmd))
    az(cmd)

    print(red_color_wrapper("command is dsdfsdfsadfsadfasf"))
    return resource_group


def check_storage_account(cmd):
    storage_account = prompt(msg="Please specify the storage account name to create or existing storage account name: ",
                             level='Question')
    #storage_account ='tckftakf'
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
    output_header()
    # Start creating storage account
    logger.warning("To init with storage module, we will start from creating storage account.")

    # Check existence of storage account
    storage_account, ans = check_storage_account(cmd)
    while ans is 'n':
        storage_account, ans = check_storage_account(cmd)
        if ans.lower() in ["q", "quit"]:
            break

    # Check existence of storage account


def output_header():
    import colorama
    header = '''
 .d8888b.  888                                              
d88P  Y88b 888                                              
Y88b.      888                                              
 "Y888b.   888888 .d88b.  888d888 8888b.   .d88b.   .d88b.  
    "Y88b. 888   d88""88b 888P"      "88b d88P"88b d8P  Y8b 
      "888 888   888  888 888    .d888888 888  888 88888888 
Y88b  d88P Y88b. Y88..88P 888    888  888 Y88b 888 Y8b.     
 "Y8888P"   "Y888 "Y88P"  888    "Y888888  "Y88888  "Y8888  
                                               888          
                                          Y8b d88P          
                                           "Y88P"
'''
    msg = "{}{}{}".format(colorama.Fore.LIGHTWHITE_EX, header, colorama.Style.RESET_ALL)
    print(msg)

def red_color_wrapper(msg):
    import colorama
    return '{}{}{}'.format(colorama.Fore.BLACK+ colorama.Back.LIGHTRED_EX, msg, colorama.Style.RESET_ALL)

