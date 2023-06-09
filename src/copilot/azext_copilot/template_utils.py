from ._constants import CREATE_APP_TEMPLATE, CREATE_STORAGE_TEMPLATE, DEFAULT_RESOURCE_GROUP, DEFAULT_RESOURCE_GROUP_NAME
from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
import os

def get_resource_client(subscription_id):
    credential = AzureCliCredential()
    subscription_id = subscription_id
    resource_client = ResourceManagementClient(credential, subscription_id)
    return resource_client

def get_storage_client(subscription_id):
    credential = AzureCliCredential()
    storage_client = StorageManagementClient(credential, subscription_id)
    return storage_client

def get_resource_group_list(resource_client):
    group_list = list(resource_client.resource_groups.list())

    groups = []
    for group in group_list[:2]:
        groups.append(f"{'{'}\n\"id\": \"{group.id}\",\n\"location\": \"{group.location}\", \n\"name\": \"{group.name}\"\n{'}'}")
    
    group_list_str = "\n".join(groups)
    # add default?
    return group_list_str, list(group_list)[0].name

def get_app_service_plan_list(resource_client, resource_group):
    plan_list = list(resource_client.resources.list_by_resource_group(resource_group, filter = "resourceType eq 'Microsoft.Web/serverFarms'"))

    plans = []
    for plan in plan_list[:2]:
        plans.append(f"{'{'}\n\"id\": \"{plan.id}\",\n\"location\": \"{plan.location}\", \n\"kind\": \"{plan.kind}\", \n\"sku\": {'{'}\n \"tier\": \"{plan.sku.tier}\"\n{'}'}\n{'}'}")
    
    plan_list_str = "\n".join(plans)
    # add default?
    return plan_list_str

def create_app_template(subscription_id, use_default=True):
    resource_client = get_resource_client(subscription_id)
    if not use_default:
        group_list, rg_name = get_resource_group_list(resource_client)
    else:
        group_list = DEFAULT_RESOURCE_GROUP
        rg_name = DEFAULT_RESOURCE_GROUP_NAME
    plan_list_str = get_app_service_plan_list(resource_client, rg_name)
    template = CREATE_APP_TEMPLATE.format(
        subscription_id=subscription_id,
        resource_group_list=group_list,
        app_service_plan_list=plan_list_str,
    )
    return template

def get_storage_sku_list(storage_client):
    sku_list = list(storage_client.skus.list())
    skus = []

    for sku in sku_list[:3]:
        locations = "[\"" +  "\", \"".join(sku.locations) + "\"]"
        skus.append(f"{'{'}\n\"name\": \"{sku.name}\", \n\"kind\": \"{sku.kind}\", \n\"tier\": \"{sku.tier}\", \n \"locations\": {locations}\n{'}'}")
    
    sku_list_str = "\n".join(skus)
    return sku_list_str

def create_storage_template(subscription_id, use_default=True):
    storage_client = get_storage_client(subscription_id)
    if not use_default:
        resource_client = get_resource_client(subscription_id)
        group_list, _ = get_resource_group_list(resource_client)
    else:
        group_list = DEFAULT_RESOURCE_GROUP
    sku_list_str = get_storage_sku_list(storage_client)
    template = CREATE_STORAGE_TEMPLATE.format(
        subscription_id=subscription_id,
        resource_group_list=group_list,
        storage_sku_list=sku_list_str
    )
    return template

def create_connection_template():
    pass

get_template = {
    'create resource': {
        'web app': create_app_template,
        'storage': create_storage_template,
    },
    'connect resources': {
        
    }
}
