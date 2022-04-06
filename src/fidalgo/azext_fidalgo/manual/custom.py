# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from azure.cli.core.util import sdk_no_wait

# customized control plane commands (these will override the generated as they are imported second)

def fidalgo_dev_center_create(client,
                              resource_group_name,
                              dev_center_name,
                              location,
                              tags=None,
                              network_connections=None,
                              identity_type="SystemAssigned",
                              user_assigned_identity=None,
                              no_wait=False):
    body = {}
    if tags is not None:
        body['tags'] = tags
    body['location'] = location
    if network_connections is not None:
        body['network_connections'] = network_connections
    body['identity'] = {}
    if identity_type is not None:
        body['identity']['type'] = identity_type
    if user_assigned_identity is not None:
        body['identity']['user_assigned_identities'] = {}
        body['identity']['user_assigned_identities'][user_assigned_identity] = {}
    if len(body['identity']) == 0:
        del body['identity']
    return sdk_no_wait(no_wait,
                       client.begin_create_or_update,
                       resource_group_name=resource_group_name,
                       dev_center_name=dev_center_name,
                       body=body)

def fidalgo_pool_create(client,
                        resource_group_name,
                        project_name,
                        pool_name,
                        location,
                        tags=None,
                        dev_box_definition_name=None,
                        network_connection_name=None,
                        no_wait=False):
    body = {}
    if tags is not None:
        body['tags'] = tags
    body['location'] = location
    if dev_box_definition_name is not None:
        body['dev_box_definition_name'] = dev_box_definition_name
    if network_connection_name is not None:
        body['network_connection_name'] = network_connection_name
    return sdk_no_wait(no_wait,
                       client.begin_create_or_update,
                       resource_group_name=resource_group_name,
                       project_name=project_name,
                       pool_name=pool_name,
                       body=body)

def fidalgo_pool_update(client,
                        resource_group_name,
                        project_name,
                        pool_name,
                        tags=None,
                        location=None,
                        dev_box_definition_name=None,
                        network_connection_name=None,
                        no_wait=False):
    body = {}
    if tags is not None:
        body['tags'] = tags
    if location is not None:
        body['location'] = location
    if dev_box_definition_name is not None:
        body['dev_box_definition_name'] = dev_box_definition_name
    if network_connection_name is not None:
        body['network_connection_name'] = network_connection_name
    return sdk_no_wait(no_wait,
                       client.begin_update,
                       resource_group_name=resource_group_name,
                       project_name=project_name,
                       pool_name=pool_name,
                       body=body)

def fidalgo_dev_box_definition_create(client,
                                      resource_group_name,
                                      dev_center_name,
                                      dev_box_definition_name,
                                      location,
                                      tags=None,
                                      image_reference=None,
                                      sku_name=None,
                                      no_wait=False):
    body = {}
    if tags is not None:
        body['tags'] = tags
    body['location'] = location
    if image_reference is not None:
        body['image_reference'] = image_reference
    body['sku'] = {}
    if sku_name is not None:
        body['sku']['name'] = sku_name
    if len(body['sku']) == 0:
        del body['sku']
    return sdk_no_wait(no_wait,
                       client.begin_create_or_update,
                       resource_group_name=resource_group_name,
                       dev_center_name=dev_center_name,
                       dev_box_definition_name=dev_box_definition_name,
                       body=body)

def fidalgo_dev_box_definition_update(client,
                                      resource_group_name,
                                      dev_center_name,
                                      dev_box_definition_name,
                                      tags=None,
                                      location=None,
                                      image_reference=None,
                                      sku_name=None,
                                      no_wait=False):
    body = {}
    if tags is not None:
        body['tags'] = tags
    if location is not None:
        body['location'] = location
    if image_reference is not None:
        body['image_reference'] = image_reference
    body['sku'] = {}
    if sku_name is not None:
        body['sku']['name'] = sku_name
    if len(body['sku']) == 0:
        del body['sku']
    return sdk_no_wait(no_wait,
                       client.begin_update,
                       resource_group_name=resource_group_name,
                       dev_center_name=dev_center_name,
                       dev_box_definition_name=dev_box_definition_name,
                       body=body)

# dataplane commands
def fidalgo_project_list_dp(client,
                dev_center,
                fidalgo_dns_suffix=None,
                top=None,
                filter_=None):
    return client.list_by_dev_center(dev_center=dev_center,
                                     fidalgo_dns_suffix=get_dns_suffix(fidalgo_dns_suffix),
                                     top=top,
                                     filter=filter_)


def fidalgo_pool_list_dp(client,
                      project_name,
                      dev_center,
                      fidalgo_dns_suffix=None,
                      top=None,
                      filter_=None):
    return client.list(dev_center=dev_center,
                       fidalgo_dns_suffix=get_dns_suffix(fidalgo_dns_suffix),
                       top=top,
                       filter=filter_,
                       project_name=project_name)


def fidalgo_pool_show_dp(client,
                      pool_name,
                      project_name,
                      dev_center,
                      fidalgo_dns_suffix=None):
    return client.get(pool_name=pool_name,
                      project_name=project_name,
                      dev_center=dev_center,
                      fidalgo_dns_suffix=get_dns_suffix(fidalgo_dns_suffix))


def fidalgo_virtual_machine_list(client,
                                 dev_center,
                                 fidalgo_dns_suffix=None,
                                 filter_=None,
                                 top=None,
                                 project_name=None,
                                 user_id=None):
    if project_name is not None:
        if user_id is None:
            user_id = 'me'
        return client.list_by_project(filter=filter_,
                                      top=top,
                                      project_name=project_name,
                                      user_id=user_id,
                                      dev_center=dev_center,
                                      fidalgo_dns_suffix=get_dns_suffix(fidalgo_dns_suffix))
    return client.list(filter=filter_,
                       top=top,
                       dev_center=dev_center,
                       fidalgo_dns_suffix=get_dns_suffix(fidalgo_dns_suffix))


def fidalgo_virtual_machine_show(client,
                                 project_name,
                                 virtual_machine_name,
                                 dev_center,
                                 user_id='me',
                                 fidalgo_dns_suffix=None):
    return client.get(project_name=project_name,
                      user_id=user_id,
                      virtual_machine_name=virtual_machine_name,
                      dev_center=dev_center,
                      fidalgo_dns_suffix=get_dns_suffix(fidalgo_dns_suffix))


def fidalgo_virtual_machine_create(client,
                                   project_name,
                                   virtual_machine_name,
                                   pool_name,
                                   dev_center,
                                   user_id='me',
                                   fidalgo_dns_suffix=None):
    body = {}
    body['pool_name'] = pool_name
    return client.create(project_name=project_name,
                         user_id=user_id,
                         virtual_machine_name=virtual_machine_name,
                         body=body,
                         dev_center=dev_center,
                         fidalgo_dns_suffix=get_dns_suffix(fidalgo_dns_suffix))


def fidalgo_virtual_machine_delete(client,
                                   project_name,
                                   virtual_machine_name,
                                   dev_center,
                                   user_id='me',
                                   fidalgo_dns_suffix=None):
    return client.delete(project_name=project_name,
                         user_id=user_id,
                         virtual_machine_name=virtual_machine_name,
                         dev_center=dev_center,
                         fidalgo_dns_suffix=get_dns_suffix(fidalgo_dns_suffix))


def fidalgo_virtual_machine_get_remote_connection(client,
                                                 project_name,
                                                 virtual_machine_name,
                                                 dev_center,
                                                 user_id='me',
                                                 fidalgo_dns_suffix=None):
    return client.get_remote_connection(project_name=project_name,
                                        user_id=user_id,
                                        virtual_machine_name=virtual_machine_name,
                                        dev_center=dev_center,
                                        fidalgo_dns_suffix=get_dns_suffix(fidalgo_dns_suffix))


def fidalgo_virtual_machine_start(client,
                                  project_name,
                                  virtual_machine_name,
                                  dev_center,
                                  user_id='me',
                                  fidalgo_dns_suffix=None):
    return client.start(project_name=project_name,
                        user_id=user_id,
                        virtual_machine_name=virtual_machine_name,
                        dev_center=dev_center,
                        fidalgo_dns_suffix=get_dns_suffix(fidalgo_dns_suffix))


def fidalgo_virtual_machine_stop(client,
                                 project_name,
                                 virtual_machine_name,
                                 dev_center,
                                 user_id='me',
                                 fidalgo_dns_suffix=None):
    return client.stop(project_name=project_name,
                       user_id=user_id,
                       virtual_machine_name=virtual_machine_name,
                       dev_center=dev_center,
                       fidalgo_dns_suffix=get_dns_suffix(fidalgo_dns_suffix))

def fidalgo_environment_list_dp(client,
                             dev_center,
                             fidalgo_dns_suffix,
                             project_name,
                             top=None):
    return client.list_by_project(dev_center=dev_center,
                                  fidalgo_dns_suffix=get_dns_suffix(fidalgo_dns_suffix),
                                  top=top,
                                  project_name=project_name)


def fidalgo_environment_show_dp(client,
                             dev_center,
                             fidalgo_dns_suffix,
                             project_name,
                             environment_name):
    return client.get(dev_center=dev_center,
                      fidalgo_dns_suffix=get_dns_suffix(fidalgo_dns_suffix),
                      project_name=project_name,
                      environment_name=environment_name)


def fidalgo_environment_create_dp(client,
                               dev_center,
                               fidalgo_dns_suffix,
                               project_name,
                               environment_name,
                               environment_type,
                               description=None,
                               catalog_item_name=None,
                               deployment_parameters=None,
                               owner=None,
                               tags=None):
    body = {}
    if description is not None:
        body['description'] = description
    if catalog_item_name is not None:
        body['catalog_item_name'] = catalog_item_name
    if deployment_parameters is not None:
        body['deployment_parameters'] = deployment_parameters
    body['environment_type'] = environment_type
    if owner is not None:
        body['owner'] = owner
    if tags is not None:
        body['tags'] = tags
    return client.create_or_update(dev_center=dev_center,
                                   fidalgo_dns_suffix=get_dns_suffix(fidalgo_dns_suffix),
                                   project_name=project_name,
                                   environment_name=environment_name,
                                   body=body)


def fidalgo_environment_update_dp(client,
                               dev_center,
                               fidalgo_dns_suffix,
                               project_name,
                               environment_name,
                               description=None,
                               catalog_item_name=None,
                               deployment_parameters=None):
    body = {}
    if description is not None:
        body['description'] = description
    if catalog_item_name is not None:
        body['catalog_item_name'] = catalog_item_name
    if deployment_parameters is not None:
        body['deployment_parameters'] = deployment_parameters
    return client.update(dev_center=dev_center,
                         fidalgo_dns_suffix=get_dns_suffix(fidalgo_dns_suffix),
                         project_name=project_name,
                         environment_name=environment_name,
                         body=body)


def fidalgo_environment_delete_dp(client,
                               dev_center,
                               fidalgo_dns_suffix,
                               project_name,
                               environment_name):
    return client.delete(dev_center=dev_center,
                         fidalgo_dns_suffix=get_dns_suffix(fidalgo_dns_suffix),
                         project_name=project_name,
                         environment_name=environment_name)


def fidalgo_environment_deploy_dp(client,
                               dev_center,
                               fidalgo_dns_suffix,
                               project_name,
                               environment_name,
                               parameters=None):
    deployment = {}
    if parameters is not None:
        deployment['parameters'] = parameters
    return client.deploy(dev_center=dev_center,
                         fidalgo_dns_suffix=get_dns_suffix(fidalgo_dns_suffix),
                         project_name=project_name,
                         environment_name=environment_name,
                         deployment=deployment)


def fidalgo_deployment_list_dp(client,
                            dev_center,
                            fidalgo_dns_suffix,
                            project_name,
                            environment_name,
                            top=None):
    return client.list_by_environment(dev_center=dev_center,
                                      fidalgo_dns_suffix=get_dns_suffix(fidalgo_dns_suffix),
                                      project_name=project_name,
                                      environment_name=environment_name,
                                      top=top)


def fidalgo_catalog_item_list_dp(client,
                              dev_center,
                              fidalgo_dns_suffix,
                              project_name,
                              top=None):
    return client.list_by_project(dev_center=dev_center,
                                  fidalgo_dns_suffix=get_dns_suffix(fidalgo_dns_suffix),
                                  project_name=project_name,
                                  top=top)

def fidalgo_environment_type_list_dp(client,
                project_name,
                dev_center,
                fidalgo_dns_suffix=None,
                top=None):
    return client.list_by_project(dev_center=dev_center,
                                project_name=project_name,
                                fidalgo_dns_suffix=get_dns_suffix(fidalgo_dns_suffix),
                                top=top)


# todo: how to pass optional arg so we don't have to redefine the dns suffix here?
def get_dns_suffix(user_provided_value):
    if user_provided_value == None:
        return 'devcenters.fidalgo.azure.com'
    else:
        return user_provided_value
