# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.util import sdk_no_wait
from ._client_factory import cf_devcenter_dataplane

# customized control plane commands (these will override the generated as they are imported second)


def devcenter_dev_center_list(client,
                              resource_group_name=None):
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name=resource_group_name)
    return client.list_by_subscription()


def devcenter_dev_center_create(
    client,
    resource_group_name,
    dev_center_name,
    location,
    tags=None,
    identity_type="SystemAssigned",
    user_assigned_identities=None,
    no_wait=False,
):
    body = {}
    if tags is not None:
        body["tags"] = tags
    body["location"] = location
    body["identity"] = {}
    if identity_type is not None:
        body["identity"]["type"] = identity_type
    if user_assigned_identities is not None:
        body['identity']['user_assigned_identities'] = user_assigned_identities
    if len(body["identity"]) == 0:
        del body["identity"]
    return sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        resource_group_name=resource_group_name,
        dev_center_name=dev_center_name,
        body=body,
    )


def devcenter_project_list(client,
                           resource_group_name=None):
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name=resource_group_name)
    return client.list_by_subscription()


def devcenter_attached_network_list(client,
                                    resource_group_name,
                                    project_name=None,
                                    dev_center_name=None):
    if project_name is not None:
        return client.list_by_project(resource_group_name=resource_group_name,
                                      project_name=project_name)
    return client.list_by_dev_center(resource_group_name=resource_group_name,
                                     dev_center_name=dev_center_name)


def devcenter_gallery_list(client,
                           resource_group_name,
                           dev_center_name):
    return client.list_by_dev_center(resource_group_name=resource_group_name,
                                     dev_center_name=dev_center_name)


def devcenter_image_list(client,
                         resource_group_name,
                         dev_center_name,
                         gallery_name=None):
    if dev_center_name is not None and gallery_name is not None:
        return client.list_by_gallery(resource_group_name=resource_group_name,
                                      dev_center_name=dev_center_name,
                                      gallery_name=gallery_name)
    return client.list_by_dev_center(resource_group_name=resource_group_name,
                                     dev_center_name=dev_center_name)


def devcenter_catalog_list(client,
                           resource_group_name,
                           dev_center_name):
    return client.list_by_dev_center(resource_group_name=resource_group_name,
                                     dev_center_name=dev_center_name)


def devcenter_environment_type_list(client,
                                    resource_group_name,
                                    dev_center_name):
    return client.list_by_dev_center(resource_group_name=resource_group_name,
                                     dev_center_name=dev_center_name)


def devcenter_project_allowed_environment_type_list(client,
                                                    resource_group_name,
                                                    project_name):
    return client.list(resource_group_name=resource_group_name,
                       project_name=project_name)


def devcenter_project_environment_type_list(client,
                                            resource_group_name,
                                            project_name):
    return client.list(resource_group_name=resource_group_name,
                       project_name=project_name)


def devcenter_dev_box_definition_list(client,
                                      resource_group_name,
                                      dev_center_name=None,
                                      project_name=None):
    if dev_center_name is not None:
        return client.list_by_dev_center(resource_group_name=resource_group_name,
                                         dev_center_name=dev_center_name)
    return client.list_by_project(resource_group_name=resource_group_name,
                                  project_name=project_name)


def devcenter_sku_list(client):
    return client.list_by_subscription()


def devcenter_pool_list(client,
                        resource_group_name,
                        project_name):
    return client.list_by_project(resource_group_name=resource_group_name,
                                  project_name=project_name)


def devcenter_network_connection_list(client,
                                      resource_group_name=None):
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name=resource_group_name)
    return client.list_by_subscription()


def devcenter_network_connection_list_health_detail(client,
                                                    resource_group_name,
                                                    network_connection_name):
    return client.list_health_details(resource_group_name=resource_group_name,
                                      network_connection_name=network_connection_name)


def devcenter_pool_create(
    client,
    resource_group_name,
    project_name,
    pool_name,
    location,
    dev_box_definition_name,
    network_connection_name,
    local_administrator,
    license_type,
    tags=None,
    no_wait=False,
):
    body = {}
    if tags is not None:
        body["tags"] = tags
    body["location"] = location
    body["dev_box_definition_name"] = dev_box_definition_name
    body["network_connection_name"] = network_connection_name
    body["license_type"] = license_type
    body["local_administrator"] = local_administrator
    return sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        resource_group_name=resource_group_name,
        project_name=project_name,
        pool_name=pool_name,
        body=body,
    )


def devcenter_pool_update(
    client,
    resource_group_name,
    project_name,
    pool_name,
    tags=None,
    location=None,
    dev_box_definition_name=None,
    network_connection_name=None,
    local_administrator=None,
    license_type=None,
    no_wait=False,
):
    body = {}
    if tags is not None:
        body["tags"] = tags
    if location is not None:
        body["location"] = location
    if dev_box_definition_name is not None:
        body["dev_box_definition_name"] = dev_box_definition_name
    if network_connection_name is not None:
        body["network_connection_name"] = network_connection_name
    if license_type is not None:
        body["license_type"] = license_type
    if local_administrator is not None:
        body["local_administrator"] = local_administrator
    return sdk_no_wait(
        no_wait,
        client.begin_update,
        resource_group_name=resource_group_name,
        project_name=project_name,
        pool_name=pool_name,
        body=body,
    )


def devcenter_schedule_show(client,
                            resource_group_name,
                            project_name,
                            pool_name):
    return client.get(resource_group_name=resource_group_name,
                      project_name=project_name,
                      pool_name=pool_name,
                      schedule_name="default")


def devcenter_schedule_create(
    client,
    resource_group_name,
    project_name,
    pool_name,
    schedule_type,
    frequency,
    time=None,
    time_zone=None,
    state=None,
    no_wait=False,
):
    body = {}
    body["type_properties_type"] = schedule_type  # "StopDevBox"
    body["frequency"] = frequency  # "Daily"
    if time is not None:
        body["time"] = time
    if time_zone is not None:
        body["time_zone"] = time_zone
    if state is not None:
        body["state"] = state
    return sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        resource_group_name=resource_group_name,
        project_name=project_name,
        pool_name=pool_name,
        schedule_name="default",
        body=body,
    )


def devcenter_schedule_update(client,
                              resource_group_name,
                              project_name,
                              pool_name,
                              schedule_type=None,
                              frequency=None,
                              time=None,
                              time_zone=None,
                              state=None,
                              no_wait=False):
    body = {}
    if schedule_type is not None:
        body["type_properties_type"] = schedule_type  # "StopDevBox"
    if frequency is not None:
        body["frequency"] = frequency  # "Daily"
    if time is not None:
        body['time'] = time
    if time_zone is not None:
        body['time_zone'] = time_zone
    if state is not None:
        body['state'] = state
    return sdk_no_wait(no_wait,
                       client.begin_update,
                       resource_group_name=resource_group_name,
                       project_name=project_name,
                       pool_name=pool_name,
                       schedule_name="default",
                       body=body)


def devcenter_schedule_delete(client,
                              resource_group_name,
                              project_name,
                              pool_name,
                              no_wait=False):
    return sdk_no_wait(no_wait,
                       client.begin_delete,
                       resource_group_name=resource_group_name,
                       project_name=project_name,
                       pool_name=pool_name,
                       schedule_name="default")


# dataplane commands
def devcenter_project_list_dp(cmd, dev_center):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center)
    return cf_dataplane.project.list()


def devcenter_project_show_dp(cmd, dev_center, project_name):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.project.get(project_name=project_name)


def devcenter_pool_list_dp(cmd, dev_center, project_name):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.pool.list()


def devcenter_pool_show_dp(cmd, dev_center, project_name, pool_name):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.pool.get(pool_name=pool_name)


def devcenter_schedule_list_dp(
    cmd, dev_center, project_name, pool_name
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.schedule.list(pool_name=pool_name)


def devcenter_schedule_show_dp(cmd, dev_center, project_name, pool_name, schedule_name):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.schedule.get(pool_name=pool_name, schedule_name=schedule_name
    )


def devcenter_dev_box_list(
    cmd, dev_center, project_name=None, user_id=None
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    if project_name is not None and user_id is not None:
        return cf_dataplane.dev_box.list_by_project(
            user_id=user_id
        )
    if user_id is not None:
        return cf_dataplane.dev_box.list_by_user(user_id=user_id)
    return cf_dataplane.dev_box.list()


def devcenter_dev_box_show(cmd, dev_center, project_name, user_id, dev_box_name):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.dev_box.get(user_id=user_id, dev_box_name=dev_box_name
    )


def devcenter_dev_box_create(
    cmd, dev_center, project_name, dev_box_name, pool_name, user_id, no_wait=False,  local_administrator=None
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    body = {}
    body["pool_name"] = pool_name
    if local_administrator is not None:
        body['local_administrator'] = local_administrator    
    return sdk_no_wait(
        no_wait,
        cf_dataplane.dev_box.begin_create,
        user_id=user_id,
        dev_box_name=dev_box_name,
        body=body,
    )


def devcenter_dev_box_delete(
    cmd, dev_center, project_name, user_id, dev_box_name, no_wait=False
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return sdk_no_wait(
        no_wait,
        cf_dataplane.dev_box.begin_delete,
        user_id=user_id,
        dev_box_name=dev_box_name,
    )


def devcenter_dev_box_get_remote_connection(
    cmd, dev_center, project_name, user_id, dev_box_name
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.dev_box.get_remote_connection(
        user_id=user_id, dev_box_name=dev_box_name
    )


def devcenter_dev_box_start(
    cmd, dev_center, project_name, user_id, dev_box_name, no_wait=False
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return sdk_no_wait(
        no_wait,
        cf_dataplane.dev_box.begin_start,
        user_id=user_id,
        dev_box_name=dev_box_name,
    )


def devcenter_dev_box_stop(
    cmd, dev_center, project_name, user_id, dev_box_name, no_wait=False, hibernate=None
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return sdk_no_wait(
        no_wait,
        cf_dataplane.dev_box.begin_stop,
        user_id=user_id,
        dev_box_name=dev_box_name,
        hibernate=hibernate
    )


def devcenter_dev_box_delay_upcoming_action(cmd, dev_center, project_name,
                                            user_id,
                                            dev_box_name,
                                            upcoming_action_id,
                                            delay_until):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.dev_box.delay_upcoming_action(user_id=user_id,
                                        dev_box_name=dev_box_name,
                                        upcoming_action_id=upcoming_action_id,
                                        delay_until=delay_until)


def devcenter_dev_box_list_upcoming_action(cmd, dev_center, project_name,
                                           user_id,
                                           dev_box_name):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.dev_box.list_upcoming_actions(user_id=user_id,
                                        dev_box_name=dev_box_name)


def devcenter_dev_box_show_upcoming_action(cmd, dev_center, project_name,
                                           user_id,
                                           dev_box_name,
                                           upcoming_action_id):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.dev_box.get_upcoming_action(user_id=user_id,
                                      dev_box_name=dev_box_name,
                                      upcoming_action_id=upcoming_action_id)


def devcenter_dev_box_skip_upcoming_action(cmd, dev_center, project_name,
                                           user_id,
                                           dev_box_name,
                                           upcoming_action_id):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.dev_box.skip_upcoming_action(user_id=user_id,
                                       dev_box_name=dev_box_name,
                                       upcoming_action_id=upcoming_action_id)


def devcenter_environment_list(cmd, dev_center, project_name, user_id):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    if user_id is not None:
            return cf_dataplane.environments.list_by_project_by_user(user_id=user_id)
    return cf_dataplane.environments.list_by_project()


def devcenter_environment_show(
    cmd, dev_center, project_name, user_id, environment_name
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.environments.get(
        user_id=user_id, environment_name=environment_name
    )


def devcenter_environment_create(cmd,
                                 dev_center,
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
                                 user=None,
                                 no_wait=False):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
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
    if user is not None:
        body['user'] = user
    return sdk_no_wait(
        no_wait,
        cf_dataplane.environments.begin_create_or_update,
        user_id=user_id,
        environment_name=environment_name,
        body=body,
    )


def devcenter_environment_update(cmd,
                                             dev_center,
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
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
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
    return cf_dataplane.environments.update(user_id=user_id,
                                     environment_name=environment_name,
                                     body=body)


def devcenter_environment_delete_environment(cmd,
                                             dev_center,
                                             project_name,
                                             user_id,
                                             environment_name,
                                             no_wait=False):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return sdk_no_wait(
        no_wait,
        cf_dataplane.environments.begin_delete,
        user_id=user_id,
        environment_name=environment_name,
    )


def devcenter_environment_custom_action(
    cmd,
    dev_center,
    project_name,
    user_id,
    environment_name,
    action_id,
    parameters=None,
    no_wait=False,
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    body = {}
    body["action_id"] = action_id
    if parameters is not None:
        body["parameters"] = parameters
    return sdk_no_wait(
        no_wait,
        cf_dataplane.environments.begin_custom_action,
        user_id=user_id,
        environment_name=environment_name,
        body=body,
    )


def devcenter_environment_deploy_action(
    cmd,
    dev_center,
    project_name,
    user_id,
    environment_name,
    action_id,
    parameters=None,
    no_wait=False,
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    body = {}
    body["action_id"] = action_id
    if parameters is not None:
        body["parameters"] = parameters
    return sdk_no_wait(
        no_wait,
        cf_dataplane.environments.begin_deploy_action,
        user_id=user_id,
        environment_name=environment_name,
        body=body,
    )


def devcenter_artifact_list(
    cmd, dev_center, project_name, user_id, environment_name, artifact_path=None
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    if (user_id is not None
        and environment_name is not None
        and artifact_path is not None
    ):
        return cf_dataplane.artifacts.list_by_path(
            user_id=user_id,
            environment_name=environment_name,
            artifact_path=artifact_path,
        )
    return cf_dataplane.artifacts.list_by_environment(
        user_id=user_id, environment_name=environment_name
    )


def devcenter_catalog_item_list(cmd, dev_center, project_name):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.catalog_items.list()


def devcenter_catalog_item_show(
    cmd, dev_center, project_name, catalog_item_id
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.catalog_items.get(catalog_item_id=catalog_item_id)


def devcenter_catalog_item_version_list(
    cmd, dev_center, project_name, catalog_item_id
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.catalog_item_versions.list(
        catalog_item_id=catalog_item_id
    )


def devcenter_catalog_item_version_show(
    cmd, dev_center, project_name, catalog_item_id, version,
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.catalog_item_versions.get(
        catalog_item_id=catalog_item_id,
        version=version,
    )


def devcenter_environment_type_list_dp(cmd, dev_center, project_name):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.environment_type.list()


def devcenter_dev_center_show_notification_setting(cmd, dev_center, project_name,
                                                   user_id):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.notification_setting.get(user_id=user_id)


def devcenter_notification_setting_list_allowed_culture_dp(cmd, dev_center, project_name,
                                                                   user_id):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.notification_setting.list_allowed_cultures(user_id=user_id)


def devcenter_notification_setting_create_dp(cmd, dev_center, project_name,
                                                     user_id,
                                                     enabled,
                                                     culture,
                                                     boolean_enabled,
                                                     email_notification,
                                                     webhook_notification):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    body = {}
    body['name'] = "default"
    body['enabled'] = enabled
    body['culture'] = culture
    body['notification_type'] = {}
    body['notification_type']['dev_box_provisioning_notification'] = {}
    body['notification_type']['dev_box_provisioning_notification']['enabled'] = boolean_enabled
    body['notification_type']['dev_box_provisioning_notification']['notification_channel'] = {}
    body['notification_type']['dev_box_provisioning_notification']['notification_channel']['email_notification'] = email_notification
    body['notification_type']['dev_box_provisioning_notification']['notification_channel']['webhook_notification'] = webhook_notification
    if len(body['notification_type']['dev_box_provisioning_notification']['notification_channel']) == 0:
        del body['notification_type']['dev_box_provisioning_notification']['notification_channel']
    return cf_dataplane.notification_setting.create(user_id=user_id,
                                               body=body)
