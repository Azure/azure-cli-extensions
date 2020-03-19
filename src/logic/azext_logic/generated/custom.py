# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines

import json
from knack.util import CLIError

def logic_workflow_list(cmd, client,
                        resource_group_name=None,
                        top=None,
                        filter=None):
    if resource_group_name is not None:
        return client.list_by_resource_group(resource_group_name=resource_group_name, top=top, filter=filter)
    return client.list_by_subscription(top=top, filter=filter)


def logic_workflow_show(cmd, client,
                        resource_group_name,
                        workflow_name):
    return client.get(resource_group_name=resource_group_name, workflow_name=workflow_name)


def logic_workflow_create(cmd, client,
                          resource_group_name,
                          workflow_name,
                          input_path,
                          location=None,
                          tags=None):
    
    with open(input_path) as json_file:
        workflow = json.load(json_file)
        if 'properties' in workflow and 'definition' not in workflow['properties']:
            raise CLIError(str(json_file) + " does not contain a 'properties.definition' key")
        elif 'properties' not in workflow and 'definition' not in workflow:
            raise CLIError(str(json_file) + " does not contain a 'definition' key")
        elif 'properties' not in workflow:
             workflow = {'properties' : workflow}        
        if tags: 
            workflow['tags'] = tags
        workflow['location'] = workflow.get('location', location)
        workflow['tags'] = workflow.get('tags', tags)
        return client.create_or_update(resource_group_name=resource_group_name, workflow_name=workflow_name, workflow=workflow)


def logic_workflow_update(cmd, client,
                          resource_group_name,
                          workflow_name,
                          tags=None):
    tags = {'tags': tags}
    return client.update(resource_group_name=resource_group_name, workflow_name=workflow_name, tags=tags)

def logic_workflow_delete(cmd, client,
                          resource_group_name,
                          workflow_name):
    return client.delete(resource_group_name=resource_group_name, workflow_name=workflow_name)

def logic_integration_account_list(cmd, client,
                                   resource_group_name=None,
                                   top=None):
    if resource_group_name is not None:
        return client.list_by_resource_group(resource_group_name=resource_group_name, top=top)
    return client.list_by_subscription(top=top)


def logic_integration_account_show(cmd, client,
                                   resource_group_name,
                                   integration_account_name):
    return client.get(resource_group_name=resource_group_name, integration_account_name=integration_account_name)


def logic_integration_account_create(cmd, client,
                                     resource_group_name,
                                     integration_account_name,
                                     input_path,
                                     location=None,
                                     tags=None,
                                     sku=None,):
    with open(input_path) as integrationJson:
        integration = json.load(integrationJson)
        if 'properties' not in integration:
            raise CLIError(str(integrationJson) + " does not contain a 'properties' key")
        integration['location'] = integration.get('location', location)
        integration['tags'] = integration.get('tags', tags)
        integration['sku'] = integration.get('sku', {"name": sku})
        return client.create_or_update(resource_group_name=resource_group_name, integration_account_name=integration_account_name, integration_account=integration)

def logic_integration_account_update(cmd, client,
                                     resource_group_name,
                                     integration_account_name,
                                     sku=None,
                                     tags=None):
    update_dict = {}
    if sku:
        update_dict['sku'] = {"name": sku}
    if tags:
        update_dict['tags'] = tags
    if not update_dict:
        raise CLIError("Nothing specified to update. Either --sku or --tags must be specfied")
    return client.update(resource_group_name=resource_group_name, integration_account_name=integration_account_name, update=update_dict)


def logic_integration_account_delete(cmd, client,
                                     resource_group_name,
                                     integration_account_name):
    return client.delete(resource_group_name=resource_group_name, integration_account_name=integration_account_name)
