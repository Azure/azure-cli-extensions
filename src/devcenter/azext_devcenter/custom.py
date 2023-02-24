# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from datetime import timedelta
from azure.cli.core.util import sdk_no_wait
from ._client_factory import cf_devcenter_dataplane
from .helper import get_project_arg
from .aaz.latest.devcenter.admin.pool import (Create as _PoolCreate, List as _PoolList)

# control plane

class PoolCreate(_PoolCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.license_type._registered=False
        return args_schema
    
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        for arg_name, arg in args:
            if arg_name == "project_name":
                arg.configured_default = "project"
        return args
    
class PoolList(_PoolList):
    
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        for arg_name, arg in args:
            if arg_name == "project_name":
                arg.configured_default = "project"
        return args
        


# data plane

def devcenter_project_list_dp(cmd, dev_center):
    resource_graph_data = get_project_arg(cmd.cli_ctx, dev_center)
    if len(resource_graph_data) == 0:
        return []
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


def devcenter_schedule_list_dp(cmd, dev_center, project_name, pool_name):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.schedule.list(pool_name=pool_name)


def devcenter_schedule_show_dp(cmd, dev_center, project_name, pool_name, schedule_name):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.schedule.get(pool_name=pool_name, schedule_name=schedule_name)


def devcenter_dev_box_list(cmd, dev_center, project_name=None, user_id=None):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    if project_name is not None and user_id is not None:
        return cf_dataplane.dev_box.list_by_project(user_id=user_id)
    if user_id is not None:
        return cf_dataplane.dev_box.list_by_user(user_id=user_id)
    return cf_dataplane.dev_box.list()


def devcenter_dev_box_show(cmd, dev_center, project_name, dev_box_name, user_id='me'):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.dev_box.get(user_id=user_id, dev_box_name=dev_box_name)


def devcenter_dev_box_create(
    cmd,
    dev_center,
    project_name,
    dev_box_name,
    pool_name,
    user_id='me',
    no_wait=False,
    local_administrator=None,
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    body = {}
    body["pool_name"] = pool_name
    if local_administrator is not None:
        body["local_administrator"] = local_administrator
    return sdk_no_wait(
        no_wait,
        cf_dataplane.dev_box.begin_create,
        user_id=user_id,
        dev_box_name=dev_box_name,
        body=body,
    )


def devcenter_dev_box_delete(
    cmd, dev_center, project_name, dev_box_name, user_id='me', no_wait=False
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return sdk_no_wait(
        no_wait,
        cf_dataplane.dev_box.begin_delete,
        user_id=user_id,
        dev_box_name=dev_box_name,
    )


def devcenter_dev_box_get_remote_connection(
    cmd, dev_center, project_name, dev_box_name, user_id='me'
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.dev_box.get_remote_connection(
        user_id=user_id, dev_box_name=dev_box_name
    )


def devcenter_dev_box_start(
    cmd, dev_center, project_name, dev_box_name, user_id='me', no_wait=False
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return sdk_no_wait(
        no_wait,
        cf_dataplane.dev_box.begin_start,
        user_id=user_id,
        dev_box_name=dev_box_name,
    )


def devcenter_dev_box_stop(
    cmd, dev_center, project_name, dev_box_name, no_wait=False, hibernate=None, user_id='me'
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return sdk_no_wait(
        no_wait,
        cf_dataplane.dev_box.begin_stop,
        user_id=user_id,
        dev_box_name=dev_box_name,
        hibernate=hibernate,
    )


def devcenter_dev_box_delay_upcoming_action(
    cmd,
    dev_center,
    project_name,
    dev_box_name,
    delay_time,
    upcoming_action_id,
    user_id='me'
):
    split_time = delay_time.split(':')
    hours = int(split_time[0])
    minutes = int(split_time[1])
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    upcoming_action = cf_dataplane.dev_box.get_upcoming_action(
        user_id=user_id,
        dev_box_name=dev_box_name,
        upcoming_action_id=upcoming_action_id,
    )
    delayed_time = upcoming_action.scheduled_time + timedelta(hours=hours, minutes=minutes)
    return cf_dataplane.dev_box.delay_upcoming_action(
        user_id=user_id,
        dev_box_name=dev_box_name,
        upcoming_action_id=upcoming_action_id,
        delay_until=delayed_time,
    )


def devcenter_dev_box_list_upcoming_action(
    cmd, dev_center, project_name, dev_box_name, user_id='me'
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.dev_box.list_upcoming_actions(
        user_id=user_id, dev_box_name=dev_box_name
    )


def devcenter_dev_box_show_upcoming_action(
    cmd, dev_center, project_name, dev_box_name, upcoming_action_id, user_id='me'
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.dev_box.get_upcoming_action(
        user_id=user_id,
        dev_box_name=dev_box_name,
        upcoming_action_id=upcoming_action_id,
    )


def devcenter_dev_box_skip_upcoming_action(
    cmd, dev_center, project_name, dev_box_name, upcoming_action_id, user_id='me'
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.dev_box.skip_upcoming_action(
        user_id=user_id,
        dev_box_name=dev_box_name,
        upcoming_action_id=upcoming_action_id,
    )


def devcenter_environment_list(cmd, dev_center, project_name, user_id='me'):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    if user_id is not None:
        return cf_dataplane.environments.list_by_project_by_user(user_id=user_id)
    return cf_dataplane.environments.list_by_project()


def devcenter_environment_show(
    cmd, dev_center, project_name, environment_name, user_id='me'
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.environments.get(
        user_id=user_id, environment_name=environment_name
    )


def devcenter_environment_create(
    cmd,
    dev_center,
    project_name,
    environment_name,
    environment_type,
    description=None,
    catalog_name=None,
    catalog_item_name=None,
    parameters=None,
    scheduled_tasks=None,
    tags=None,
    user=None,
    no_wait=False,
    user_id='me'
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
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
    body["environment_type"] = environment_type
    if user is not None:
        body["user"] = user
    return sdk_no_wait(
        no_wait,
        cf_dataplane.environments.begin_create_or_update,
        user_id=user_id,
        environment_name=environment_name,
        body=body,
    )


def devcenter_environment_update(
    cmd,
    dev_center,
    project_name,
    environment_name,
    description=None,
    catalog_name=None,
    catalog_item_name=None,
    parameters=None,
    scheduled_tasks=None,
    tags=None,
    user_id=None
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    body = {}
    if user_id is None:
        user_id = "me"
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
    return cf_dataplane.environments.update(
        user_id=user_id, environment_name=environment_name, body=body
    )


def devcenter_environment_delete(
    cmd, dev_center, project_name, environment_name, no_wait=False, user_id='me'
):
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
    environment_name,
    action_id,
    parameters=None,
    no_wait=False,
    user_id='me'
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
    environment_name,
    action_id,
    parameters=None,
    no_wait=False,
    user_id='me'
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


def devcenter_catalog_item_list(cmd, dev_center, project_name):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.catalog_items.list()


def devcenter_catalog_item_show(cmd, dev_center, project_name, catalog_item_id):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.catalog_items.get(catalog_item_id=catalog_item_id)


def devcenter_catalog_item_version_list(cmd, dev_center, project_name, catalog_item_id):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.catalog_item_versions.list(catalog_item_id=catalog_item_id)


def devcenter_catalog_item_version_show(
    cmd,
    dev_center,
    project_name,
    catalog_item_id,
    version,
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.catalog_item_versions.get(
        catalog_item_id=catalog_item_id,
        version=version,
    )


def devcenter_environment_type_list_dp(cmd, dev_center, project_name):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.environment_type.list()


def devcenter_notification_setting_show_dp(
    cmd, dev_center, project_name, user_id='me'
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.notification_setting.get(user_id=user_id)


def devcenter_notification_setting_list_allowed_culture_dp(
    cmd, dev_center, project_name, user_id='me'
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.notification_setting.list_allowed_cultures(user_id=user_id)


def devcenter_notification_setting_create_dp(
    cmd,
    dev_center,
    project_name,
    enabled,
    culture,
    boolean_enabled,
    email_notification,
    webhook_notification,
    user_id='me'
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    body = {}
    body["name"] = "default"
    body["enabled"] = enabled
    body["culture"] = culture
    body["notification_type"] = {}
    body["notification_type"]["dev_box_provisioning_notification"] = {}
    body["notification_type"]["dev_box_provisioning_notification"][
        "enabled"
    ] = boolean_enabled
    body["notification_type"]["dev_box_provisioning_notification"][
        "notification_channel"
    ] = {}
    body["notification_type"]["dev_box_provisioning_notification"][
        "notification_channel"
    ]["email_notification"] = email_notification
    body["notification_type"]["dev_box_provisioning_notification"][
        "notification_channel"
    ]["webhook_notification"] = webhook_notification
    if (
        len(
            body["notification_type"]["dev_box_provisioning_notification"][
                "notification_channel"
            ]
        )
        == 0
    ):
        del body["notification_type"]["dev_box_provisioning_notification"][
            "notification_channel"
        ]
    return cf_dataplane.notification_setting.create(user_id=user_id, body=body)
