# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument

from azure.cli.core.util import sdk_no_wait


def create_monitor_log_analytics_solution(client,
                                          resource_group_name,
                                          solution_type,
                                          workspace_resource_id,
                                          location,
                                          solution_name=None,
                                          plan_publisher=None,
                                          plan_product=None,
                                          tags=None,
                                          no_wait=False):

    body = {
        'location': location,
        'tags': tags,
        'properties': {
            "workspace_resource_id": workspace_resource_id
        },
        "plan": {
            "name": solution_name,
            "product": "OMSGallery/" + solution_type,
            "publisher": "Microsoft",
            "promotion_code": ""
        }
    }

    return sdk_no_wait(no_wait, client.create_or_update, resource_group_name=resource_group_name,
                       solution_name=solution_name, parameters=body)


def update_monitor_log_analytics_solution(client,
                                          resource_group_name,
                                          solution_name,
                                          tags=None,
                                          no_wait=False):

    return sdk_no_wait(no_wait, client.update, resource_group_name=resource_group_name,
                       solution_name=solution_name, tags=tags)


def delete_monitor_log_analytics_solution(client,
                                          resource_group_name,
                                          solution_name,
                                          no_wait=False):
    return sdk_no_wait(no_wait, client.delete, resource_group_name=resource_group_name, solution_name=solution_name)


def get_monitor_log_analytics_solution(client,
                                       resource_group_name,
                                       solution_name):
    return client.get(resource_group_name=resource_group_name, solution_name=solution_name)


def list_monitor_log_analytics_solution(client, resource_group_name=None):
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name=resource_group_name)
    return client.list_by_subscription()
