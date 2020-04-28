# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument

from azure.cli.core.commands.client_factory import get_subscription_id


def create_monitor_log_analytics_solution(cmd,
                                          client,
                                          resource_group_name,
                                          solution_name,
                                          plan_publisher,
                                          plan_product,
                                          location=None,
                                          workspace_resource_id=None,
                                          workspace_name=None,
                                          tags=None):
    if workspace_name:
        reference_workspace = '/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.OperationalInsights/' \
                              'workspaces/{2}'.format(get_subscription_id(cmd.cli_ctx), resource_group_name,
                                                      workspace_name)
    else:
        reference_workspace = workspace_resource_id

    body = {
        'location': location,
        'tags': tags,
        'properties': {
            "workspace_resource_id": reference_workspace
        },
        "plan": {
            "name": solution_name,
            "product": plan_product,
            "publisher": plan_publisher,
            "promotion_code": ""
        }
    }

    return client.create_or_update(resource_group_name=resource_group_name, solution_name=solution_name, parameters=body)


def update_monitor_log_analytics_solution(client,
                                          resource_group_name,
                                          solution_name,
                                          tags=None):

    return client.update(resource_group_name=resource_group_name, solution_name=solution_name, tags=tags)


def delete_monitor_log_analytics_solution(client,
                                          resource_group_name,
                                          solution_name):
    return client.delete(resource_group_name=resource_group_name, solution_name=solution_name)


def get_monitor_log_analytics_solution(client,
                                       resource_group_name,
                                       solution_name):
    return client.get(resource_group_name=resource_group_name, solution_name=solution_name)


def list_monitor_log_analytics_solution(client, resource_group_name=None):
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name=resource_group_name)
    return client.list_by_subscription()
