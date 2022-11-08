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
    if resource_group_name and project_name is not None:
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
    if resource_group_name and dev_center_name is not None and gallery_name is not None:
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
    if resource_group_name and dev_center_name is not None:
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
    cf_devcenter = cf_devcenter_dataplane(cmd.cli_ctx, dev_center)
    return cf_devcenter.project.list_by_dev_center()


def devcenter_project_show_dp(cmd, dev_center, project_name):
    cf_devcenter = cf_devcenter_dataplane(cmd.cli_ctx, dev_center)
    return cf_devcenter.project.get(project_name=project_name)


def devcenter_pool_list_dp(cmd, dev_center, project_name):
    cf_devcenter = cf_devcenter_dataplane(cmd.cli_ctx, dev_center)
    return cf_devcenter.pool.list(project_name=project_name)


def devcenter_pool_show_dp(cmd, dev_center, project_name, pool_name):
    cf_devcenter = cf_devcenter_dataplane(cmd.cli_ctx, dev_center)
    return cf_devcenter.pool.get(project_name=project_name, pool_name=pool_name)


def devcenter_schedule_list_dp(
    cmd, dev_center, project_name, pool_name
):
    cf_devcenter = cf_devcenter_dataplane(cmd.cli_ctx, dev_center)
    return cf_devcenter.schedule.list(
        project_name=project_name, pool_name=pool_name
    )


def devcenter_schedule_show_dp(cmd, dev_center, project_name, pool_name, schedule_name):
    cf_devcenter = cf_devcenter_dataplane(cmd.cli_ctx, dev_center)
    return cf_devcenter.schedule.get(
        project_name=project_name, pool_name=pool_name, schedule_name=schedule_name
    )


def devcenter_dev_box_list(
    cmd, dev_center, filter_=None, project_name=None, user_id=None
):
    cf_devcenter = cf_devcenter_dataplane(cmd.cli_ctx, dev_center)
    if project_name is not None and user_id is not None:
        return cf_devcenter.dev_box.list_by_project(
            filter=filter_, project_name=project_name, user_id=user_id
        )
    if user_id is not None:
        return cf_devcenter.dev_box.list_by_user(filter=filter_, user_id=user_id)
    return cf_devcenter.dev_box.list(filter=filter_)


def devcenter_dev_box_show(cmd, dev_center, project_name, user_id, dev_box_name):
    cf_devcenter = cf_devcenter_dataplane(cmd.cli_ctx, dev_center)
    return cf_devcenter.dev_box.get(
        project_name=project_name, user_id=user_id, dev_box_name=dev_box_name
    )


def devcenter_dev_box_create(
    cmd, dev_center, project_name, dev_box_name, pool_name, user_id="me", no_wait=False
):
    cf_devcenter = cf_devcenter_dataplane(cmd.cli_ctx, dev_center)
    body = {}
    body["pool_name"] = pool_name
    return sdk_no_wait(
        no_wait,
        cf_devcenter.dev_box.begin_create,
        project_name=project_name,
        user_id=user_id,
        dev_box_name=dev_box_name,
        body=body,
    )


def devcenter_dev_box_delete(
    cmd, dev_center, project_name, user_id, dev_box_name, no_wait=False
):
    cf_devcenter = cf_devcenter_dataplane(cmd.cli_ctx, dev_center)
    return sdk_no_wait(
        no_wait,
        cf_devcenter.dev_box.begin_delete,
        project_name=project_name,
        user_id=user_id,
        dev_box_name=dev_box_name,
    )


def devcenter_dev_box_get_remote_connection(
    cmd, dev_center, project_name, user_id, dev_box_name
):
    cf_devcenter = cf_devcenter_dataplane(cmd.cli_ctx, dev_center)
    return cf_devcenter.dev_box.get_remote_connection(
        project_name=project_name, user_id=user_id, dev_box_name=dev_box_name
    )


def devcenter_dev_box_start(
    cmd, dev_center, project_name, user_id, dev_box_name, no_wait=False
):
    cf_devcenter = cf_devcenter_dataplane(cmd.cli_ctx, dev_center)
    return sdk_no_wait(
        no_wait,
        cf_devcenter.dev_box.begin_start,
        project_name=project_name,
        user_id=user_id,
        dev_box_name=dev_box_name,
    )


def devcenter_dev_box_stop(
    cmd, dev_center, project_name, user_id, dev_box_name, no_wait=False
):
    cf_devcenter = cf_devcenter_dataplane(cmd.cli_ctx, dev_center)
    return sdk_no_wait(
        no_wait,
        cf_devcenter.dev_box.begin_stop,
        project_name=project_name,
        user_id=user_id,
        dev_box_name=dev_box_name,
    )


def devcenter_environment_list(cmd, dev_center, project_name):
    cf_devcenter = cf_devcenter_dataplane(cmd.cli_ctx, dev_center)
    return cf_devcenter.environments.list_by_project(project_name=project_name)


def devcenter_environment_show(
    cmd, dev_center, project_name, user_id, environment_name
):
    cf_devcenter = cf_devcenter_dataplane(cmd.cli_ctx, dev_center)
    return cf_devcenter.environments.get(
        project_name=project_name, user_id=user_id, environment_name=environment_name
    )


def devcenter_environment_create(
    cmd,
    dev_center,
    project_name,
    environment_name,
    environment_type,
    catalog_name,
    catalog_item_name,
    user_id="me",
    description=None,
    parameters=None,
    scheduled_tasks=None,
    tags=None,
    owner=None,
    no_wait=False,
):
    cf_devcenter = cf_devcenter_dataplane(cmd.cli_ctx, dev_center)
    body = {}
    body["catalog_name"] = catalog_name
    body["catalog_item_name"] = catalog_item_name
    if description is not None:
        body["description"] = description
    if parameters is not None:
        body["parameters"] = parameters
    if scheduled_tasks is not None:
        body["scheduled_tasks"] = scheduled_tasks
    if tags is not None:
        body["tags"] = tags
    body["environment_type"] = environment_type
    if owner is not None:
        body["owner"] = owner
    return sdk_no_wait(
        no_wait,
        cf_devcenter.environments.begin_create_or_update,
        project_name=project_name,
        user_id=user_id,
        environment_name=environment_name,
        body=body,
    )


def devcenter_environment_update(
    cmd,
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
    no_wait=False,
):
    cf_devcenter = cf_devcenter_dataplane(cmd.cli_ctx, dev_center)
    body = {}
    if description is not None:
        body["description"] = description
    if catalog_name is not None:
        body["catalog_name"] = catalog_name
    if catalog_item_name is not None:
        body["catalog_item_name"] = catalog_item_name
    if parameters is not None:
        body["parameters"] = parameters
    if scheduled_tasks is not None:
        body["scheduled_tasks"] = scheduled_tasks
    if tags is not None:
        body["tags"] = tags
    return sdk_no_wait(
        no_wait,
        cf_devcenter.environments.begin_update,
        project_name=project_name,
        user_id=user_id,
        environment_name=environment_name,
        body=body,
    )


def devcenter_environment_delete(
    cmd, dev_center, project_name, user_id, environment_name, no_wait=False
):
    cf_devcenter = cf_devcenter_dataplane(cmd.cli_ctx, dev_center)
    return sdk_no_wait(
        no_wait,
        cf_devcenter.environments.begin_delete,
        project_name=project_name,
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
    cf_devcenter = cf_devcenter_dataplane(cmd.cli_ctx, dev_center)
    body = {}
    body["action_id"] = action_id
    if parameters is not None:
        body["parameters"] = parameters
    return sdk_no_wait(
        no_wait,
        cf_devcenter.environments.begin_custom_action,
        project_name=project_name,
        user_id=user_id,
        environment_name=environment_name,
        body=body,
    )


def devcenter_environment_delete_action(
    cmd,
    dev_center,
    project_name,
    user_id,
    environment_name,
    action_id,
    parameters=None,
    no_wait=False,
):
    cf_devcenter = cf_devcenter_dataplane(cmd.cli_ctx, dev_center)
    body = {}
    body["action_id"] = action_id
    if parameters is not None:
        body["parameters"] = parameters
    return sdk_no_wait(
        no_wait,
        cf_devcenter.environments.begin_delete_action,
        project_name=project_name,
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
    cf_devcenter = cf_devcenter_dataplane(cmd.cli_ctx, dev_center)
    body = {}
    body["action_id"] = action_id
    if parameters is not None:
        body["parameters"] = parameters
    return sdk_no_wait(
        no_wait,
        cf_devcenter.environments.begin_deploy_action,
        project_name=project_name,
        user_id=user_id,
        environment_name=environment_name,
        body=body,
    )


def devcenter_environment_list_by_project(
    cmd, dev_center, project_name, user_id
):
    cf_devcenter = cf_devcenter_dataplane(cmd.cli_ctx, dev_center)
    return cf_devcenter.environments.list_by_project_by_user(
        project_name=project_name, user_id=user_id
    )


def devcenter_artifact_list(
    cmd, dev_center, project_name, user_id, environment_name, artifact_path=None
):
    cf_devcenter = cf_devcenter_dataplane(cmd.cli_ctx, dev_center)
    if (
        project_name is not None
        and user_id is not None
        and environment_name is not None
        and artifact_path is not None
    ):
        return cf_devcenter.artifacts.list_by_path(
            project_name=project_name,
            user_id=user_id,
            environment_name=environment_name,
            artifact_path=artifact_path,
        )
    return cf_devcenter.artifacts.list_by_environment(
        project_name=project_name, user_id=user_id, environment_name=environment_name
    )


def devcenter_catalog_item_list(cmd, dev_center, project_name):
    cf_devcenter = cf_devcenter_dataplane(cmd.cli_ctx, dev_center)
    return cf_devcenter.catalog_item.list_by_project(project_name=project_name)


def devcenter_catalog_item_show(
    cmd, dev_center, project_name, catalog_item_id
):
    cf_devcenter = cf_devcenter_dataplane(cmd.cli_ctx, dev_center)
    return cf_devcenter.catalog_item.get(
        project_name=project_name, catalog_item_id=catalog_item_id
    )


def devcenter_catalog_item_version_list(
    cmd, dev_center, project_name, catalog_item_id
):
    cf_devcenter = cf_devcenter_dataplane(cmd.cli_ctx, dev_center)
    return cf_devcenter.catalog_item_versions.list_by_project(
        project_name=project_name, catalog_item_id=catalog_item_id
    )


def devcenter_catalog_item_version_show(
    cmd, dev_center, project_name, catalog_item_id, version,
):
    cf_devcenter = cf_devcenter_dataplane(cmd.cli_ctx, dev_center)
    return cf_devcenter.catalog_item_versions.get(
        project_name=project_name,
        catalog_item_id=catalog_item_id,
        version=version,
    )


def devcenter_environment_type_list_dp(cmd, dev_center, project_name):
    cf_devcenter = cf_devcenter_dataplane(cmd.cli_ctx, dev_center)
    return cf_devcenter.environment_type.list_by_project(
        project_name=project_name
    )
