# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from threading import local
from knack.util import CLIError
from azure.cli.core.util import sdk_no_wait

# customized control plane commands (these will override the generated as they are imported second)

def devcenter_dev_center_create(client,
                              resource_group_name,
                              dev_center_name,
                              location,
                              tags=None,
                              identity_type="SystemAssigned",
                              user_assigned_identity=None,
                              no_wait=False):
    body = {}
    if tags is not None:
        body['tags'] = tags
    body['location'] = location
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

def devcenter_pool_create(client,
                        resource_group_name,
                        project_name,
                        pool_name,
                        location,
                        dev_box_definition_name,
                        network_connection_name,
                        local_administrator,
                        license_type,
                        tags=None,
                        no_wait=False):
    body = {}
    if tags is not None:
        body['tags'] = tags
    body['location'] = location
    body['dev_box_definition_name'] = dev_box_definition_name
    body['network_connection_name'] = network_connection_name
    body['license_type'] = license_type
    body['local_administrator'] = local_administrator
    return sdk_no_wait(no_wait,
                       client.begin_create_or_update,
                       resource_group_name=resource_group_name,
                       project_name=project_name,
                       pool_name=pool_name,
                       body=body)

def devcenter_pool_update(client,
                        resource_group_name,
                        project_name,
                        pool_name,
                        tags=None,
                        location=None,
                        dev_box_definition_name=None,
                        network_connection_name=None,
                        local_administrator=None,
                        license_type=None,
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
    if license_type is not None:
        body['license_type'] = license_type
    if local_administrator is not None:
        body['local_administrator'] = local_administrator
    return sdk_no_wait(no_wait,
                       client.begin_update,
                       resource_group_name=resource_group_name,
                       project_name=project_name,
                       pool_name=pool_name,
                       body=body)

def devcenter_schedule_create(client,
                              resource_group_name,
                              project_name,
                              pool_name,
                              schedule_name,
                              schedule_type,
                              frequency,
                              time=None,
                              time_zone=None,
                              state=None,
                              no_wait=False):
    body = {}
    body['type_properties_type'] = schedule_type #"StopDevBox"
    body['frequency'] = frequency #"Daily"
    if time is not None:
        body['time'] = time
    if time_zone is not None:
        body['time_zone'] = time_zone
    if state is not None:
        body['state'] = state
    return sdk_no_wait(no_wait,
                       client.begin_create_or_update,
                       resource_group_name=resource_group_name,
                       project_name=project_name,
                       pool_name=pool_name,
                       schedule_name=schedule_name,
                       body=body)


# dataplane commands
def devcenter_project_list_dp(client,
                           dev_center,
                           dev_center_dns_suffix,
                           filter_=None,
                           top=None):
    return client.list_by_dev_center(dev_center=dev_center,
                                     dev_center_dns_suffix=get_dns_suffix(dev_center_dns_suffix),
                                     filter=filter_,
                                     top=top)


def devcenter_project_show_dp(client,
                           dev_center,
                           dev_center_dns_suffix,
                           project_name):
    return client.get(dev_center=dev_center,
                      dev_center_dns_suffix=get_dns_suffix(dev_center_dns_suffix),
                      project_name=project_name)


def devcenter_pool_list_dp(client,
                        dev_center,
                        dev_center_dns_suffix,
                        project_name,
                        top=None,
                        filter_=None):
    return client.list(dev_center=dev_center,
                       dev_center_dns_suffix=get_dns_suffix(dev_center_dns_suffix),
                       top=top,
                       filter=filter_,
                       project_name=project_name)


def devcenter_pool_show_dp(client,
                        dev_center,
                        dev_center_dns_suffix,
                        project_name,
                        pool_name):
    return client.get(dev_center=dev_center,
                      dev_center_dns_suffix=get_dns_suffix(dev_center_dns_suffix),
                      project_name=project_name,
                      pool_name=pool_name)


def devcenter_schedule_list_dp(client,
                            dev_center,
                            dev_center_dns_suffix,
                            project_name,
                            pool_name,
                            top=None,
                            filter_=None):
    return client.list(dev_center=dev_center,
                       dev_center_dns_suffix=get_dns_suffix(dev_center_dns_suffix),
                       top=top,
                       filter=filter_,
                       project_name=project_name,
                       pool_name=pool_name)


def devcenter_schedule_show_dp(client,
                            dev_center,
                            dev_center_dns_suffix,
                            project_name,
                            pool_name,
                            schedule_name):
    return client.get(dev_center=dev_center,
                      dev_center_dns_suffix=get_dns_suffix(dev_center_dns_suffix),
                      project_name=project_name,
                      pool_name=pool_name,
                      schedule_name=schedule_name)


def devcenter_dev_box_list(client,
                           dev_center,
                           dev_center_dns_suffix,
                           filter_=None,
                           top=None,
                           project_name=None,
                           user_id=None):
    if dev_center is not None and dev_center_dns_suffix is not None and project_name is not None and user_id is not None:
        return client.list_by_project(dev_center=dev_center,
                                      dev_center_dns_suffix=get_dns_suffix(dev_center_dns_suffix),
                                      filter=filter_,
                                      top=top,
                                      project_name=project_name,
                                      user_id=user_id)
    elif dev_center is not None and dev_center_dns_suffix is not None and user_id is not None:
        return client.list_by_user(dev_center=dev_center,
                                   dev_center_dns_suffix=get_dns_suffix(dev_center_dns_suffix),
                                   filter=filter_,
                                   top=top,
                                   user_id=user_id)
    return client.list(dev_center=dev_center,
                       dev_center_dns_suffix=get_dns_suffix(dev_center_dns_suffix),
                       filter=filter_,
                       top=top)


def devcenter_dev_box_show(client,
                           dev_center,
                           dev_center_dns_suffix,
                           project_name,
                           user_id,
                           dev_box_name):
    return client.get(dev_center=dev_center,
                      dev_center_dns_suffix=get_dns_suffix(dev_center_dns_suffix),
                      project_name=project_name,
                      user_id=user_id,
                      dev_box_name=dev_box_name)


def devcenter_dev_box_create(client,
                             dev_center,
                             dev_center_dns_suffix,
                             project_name,
                             user_id,
                             dev_box_name,
                             pool_name,
                             no_wait=False):
    body = {}
    body['pool_name'] = pool_name
    return sdk_no_wait(no_wait,
                       client.begin_create,
                       dev_center=dev_center,
                       dev_center_dns_suffix=get_dns_suffix(dev_center_dns_suffix),
                       project_name=project_name,
                       user_id=user_id,
                       dev_box_name=dev_box_name,
                       body=body)


def devcenter_dev_box_delete(client,
                             dev_center,
                             dev_center_dns_suffix,
                             project_name,
                             user_id,
                             dev_box_name,
                             no_wait=False):
    return sdk_no_wait(no_wait,
                       client.begin_delete,
                       dev_center=dev_center,
                       dev_center_dns_suffix=get_dns_suffix(dev_center_dns_suffix),
                       project_name=project_name,
                       user_id=user_id,
                       dev_box_name=dev_box_name)


def devcenter_dev_box_get_remote_connection(client,
                                            dev_center,
                                            dev_center_dns_suffix,
                                            project_name,
                                            user_id,
                                            dev_box_name):
    return client.get_remote_connection(dev_center=dev_center,
                                        dev_center_dns_suffix=get_dns_suffix(dev_center_dns_suffix),
                                        project_name=project_name,
                                        user_id=user_id,
                                        dev_box_name=dev_box_name)


def devcenter_dev_box_start(client,
                            dev_center,
                            dev_center_dns_suffix,
                            project_name,
                            user_id,
                            dev_box_name,
                            no_wait=False):
    return sdk_no_wait(no_wait,
                       client.begin_start,
                       dev_center=dev_center,
                       dev_center_dns_suffix=get_dns_suffix(dev_center_dns_suffix),
                       project_name=project_name,
                       user_id=user_id,
                       dev_box_name=dev_box_name)


def devcenter_dev_box_stop(client,
                           dev_center,
                           dev_center_dns_suffix,
                           project_name,
                           user_id,
                           dev_box_name,
                           no_wait=False):
    return sdk_no_wait(no_wait,
                       client.begin_stop,
                       dev_center=dev_center,
                       dev_center_dns_suffix=get_dns_suffix(dev_center_dns_suffix),
                       project_name=project_name,
                       user_id=user_id,
                       dev_box_name=dev_box_name)


def devcenter_environment_list(client,
                               dev_center,
                               dev_center_dns_suffix,
                               project_name,
                               top=None):
    return client.list_by_project(dev_center=dev_center,
                                  dev_center_dns_suffix=get_dns_suffix(dev_center_dns_suffix),
                                  top=top,
                                  project_name=project_name)


def devcenter_environment_show(client,
                               dev_center,
                               dev_center_dns_suffix,
                               project_name,
                               user_id,
                               environment_name):
    return client.get(dev_center=dev_center,
                      dev_center_dns_suffix=get_dns_suffix(dev_center_dns_suffix),
                      project_name=project_name,
                      user_id=user_id,
                      environment_name=environment_name)


def devcenter_environment_create(client,
                                 dev_center,
                                 dev_center_dns_suffix,
                                 project_name,
                                 user_id,
                                 environment_name,
                                 environment_type,
                                 description=None,
                                 catalog_name=None,
                                 catalog_item_name=None,
                                 parameters=None,
                                 scheduled_tasks=None,
                                 tags=None,
                                 owner=None,
                                 no_wait=False):
    body = {}
    if description is not None:
        body['description'] = description
    if catalog_name is not None:
        body['catalog_name'] = catalog_name
    if catalog_item_name is not None:
        body['catalog_item_name'] = catalog_item_name
    if parameters is not None:
        body['parameters'] = parameters
    if scheduled_tasks is not None:
        body['scheduled_tasks'] = scheduled_tasks
    if tags is not None:
        body['tags'] = tags
    body['environment_type'] = environment_type
    if owner is not None:
        body['owner'] = owner
    return sdk_no_wait(no_wait,
                       client.begin_create_or_update,
                       dev_center=dev_center,
                       dev_center_dns_suffix=get_dns_suffix(dev_center_dns_suffix),
                       project_name=project_name,
                       user_id=user_id,
                       environment_name=environment_name,
                       body=body)


def devcenter_environment_update(client,
                                 dev_center,
                                 dev_center_dns_suffix,
                                 project_name,
                                 user_id,
                                 environment_name,
                                 description=None,
                                 catalog_name=None,
                                 catalog_item_name=None,
                                 parameters=None,
                                 scheduled_tasks=None,
                                 tags=None,
                                 no_wait=False):
    body = {}
    if description is not None:
        body['description'] = description
    if catalog_name is not None:
        body['catalog_name'] = catalog_name
    if catalog_item_name is not None:
        body['catalog_item_name'] = catalog_item_name
    if parameters is not None:
        body['parameters'] = parameters
    if scheduled_tasks is not None:
        body['scheduled_tasks'] = scheduled_tasks
    if tags is not None:
        body['tags'] = tags
    return sdk_no_wait(no_wait,
                       client.begin_update,
                       dev_center=dev_center,
                       dev_center_dns_suffix=get_dns_suffix(dev_center_dns_suffix),
                       project_name=project_name,
                       user_id=user_id,
                       environment_name=environment_name,
                       body=body)


def devcenter_environment_delete(client,
                                 dev_center,
                                 dev_center_dns_suffix,
                                 project_name,
                                 user_id,
                                 environment_name,
                                 no_wait=False):
    return sdk_no_wait(no_wait,
                       client.begin_delete,
                       dev_center=dev_center,
                       dev_center_dns_suffix=get_dns_suffix(dev_center_dns_suffix),
                       project_name=project_name,
                       user_id=user_id,
                       environment_name=environment_name)


def devcenter_environment_list_by_project(client,
                                          dev_center,
                                          dev_center_dns_suffix,
                                          project_name,
                                          user_id,
                                          top=None):
    return client.list_by_project_by_user(dev_center=dev_center,
                                          dev_center_dns_suffix=get_dns_suffix(dev_center_dns_suffix),
                                          top=top,
                                          project_name=project_name,
                                          user_id=user_id)


def devcenter_action_list(client,
                          dev_center,
                          dev_center_dns_suffix,
                          project_name,
                          user_id,
                          environment_name,
                          top=None):
    return client.list_by_environment(dev_center=dev_center,
                                      dev_center_dns_suffix=get_dns_suffix(dev_center_dns_suffix),
                                      project_name=project_name,
                                      user_id=user_id,
                                      environment_name=environment_name,
                                      top=top)


def devcenter_action_show(client,
                          dev_center,
                          dev_center_dns_suffix,
                          project_name,
                          user_id,
                          environment_name,
                          action_id):
    return client.get(dev_center=dev_center,
                      dev_center_dns_suffix=get_dns_suffix(dev_center_dns_suffix),
                      project_name=project_name,
                      user_id=user_id,
                      environment_name=environment_name,
                      action_id=action_id)


def devcenter_action_create(client,
                            dev_center,
                            dev_center_dns_suffix,
                            project_name,
                            user_id,
                            environment_name,
                            action_id,
                            parameters=None,
                            no_wait=False):
    action = {}
    action['action_id'] = action_id
    if parameters is not None:
        action['parameters'] = parameters
    return sdk_no_wait(no_wait,
                       client.begin_create,
                       dev_center=dev_center,
                       dev_center_dns_suffix=get_dns_suffix(dev_center_dns_suffix),
                       project_name=project_name,
                       user_id=user_id,
                       environment_name=environment_name,
                       action=action)


def devcenter_artifact_list(client,
                            dev_center,
                            dev_center_dns_suffix,
                            project_name,
                            user_id,
                            environment_name,
                            artifact_path=None):
    if dev_center is not None and dev_center_dns_suffix is not None and project_name is not None and user_id is not None and environment_name is not None and artifact_path is not None:
        return client.list_by_path(dev_center=dev_center,
                                   dev_center_dns_suffix=get_dns_suffix(dev_center_dns_suffix),
                                   project_name=project_name,
                                   user_id=user_id,
                                   environment_name=environment_name,
                                   artifact_path=artifact_path)
    return client.list_by_environment(dev_center=dev_center,
                                      dev_center_dns_suffix=get_dns_suffix(dev_center_dns_suffix),
                                      project_name=project_name,
                                      user_id=user_id,
                                      environment_name=environment_name)


def devcenter_catalog_item_list(client,
                                dev_center,
                                dev_center_dns_suffix,
                                project_name,
                                top=None):
    return client.list_by_project(dev_center=dev_center,
                                  dev_center_dns_suffix=get_dns_suffix(dev_center_dns_suffix),
                                  project_name=project_name,
                                  top=top)


def devcenter_catalog_item_show(client,
                                dev_center,
                                dev_center_dns_suffix,
                                project_name,
                                catalog_item_id,
                                top=None):
    return client.get(dev_center=dev_center,
                      dev_center_dns_suffix=get_dns_suffix(dev_center_dns_suffix),
                      project_name=project_name,
                      top=top,
                      catalog_item_id=catalog_item_id)


def devcenter_catalog_item_version_list(client,
                                        dev_center,
                                        dev_center_dns_suffix,
                                        project_name,
                                        catalog_item_id,
                                        top=None):
    return client.list_by_project(dev_center=dev_center,
                                  dev_center_dns_suffix=get_dns_suffix(dev_center_dns_suffix),
                                  project_name=project_name,
                                  top=top,
                                  catalog_item_id=catalog_item_id)


def devcenter_catalog_item_version_show(client,
                                        dev_center,
                                        dev_center_dns_suffix,
                                        project_name,
                                        catalog_item_id,
                                        version,
                                        top=None):
    return client.get(dev_center=dev_center,
                      dev_center_dns_suffix=get_dns_suffix(dev_center_dns_suffix),
                      project_name=project_name,
                      top=top,
                      catalog_item_id=catalog_item_id,
                      version=version)


def devcenter_environment_type_list_dp(client,
                                    dev_center,
                                    dev_center_dns_suffix,
                                    project_name,
                                    top=None):
    return client.list_by_project(dev_center=dev_center,
                                  dev_center_dns_suffix=get_dns_suffix(dev_center_dns_suffix),
                                  project_name=project_name,
                                  top=top)


# todo: how to pass optional arg so we don't have to redefine the dns suffix here?
def get_dns_suffix(user_provided_value):
    if user_provided_value == None:
        return 'devcenter.azure.com'
    else:
        return user_provided_value
