# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines

import json


def portal_dashboard_list(cmd, client,
                          resource_group_name=None):
    if resource_group_name is not None:
        return client.list_by_resource_group(resource_group_name=resource_group_name)
    return client.list_by_subscription()


def portal_dashboard_show(cmd, client,
                          resource_group_name,
                          name):
    return client.get(resource_group_name=resource_group_name, dashboard_name=name)


def portal_dashboard_create(cmd, client,
                            resource_group_name,
                            name,
                            location,
                            tags=None,
                            properties_lenses=None,
                            properties_metadata=None):
    properties_lenses = json.loads(properties_lenses) if isinstance(properties_lenses, str) else properties_lenses
    return client.create_or_update(resource_group_name=resource_group_name, dashboard_name=name, location=location, tags=tags, lenses=properties_lenses, metadata=properties_metadata)


def portal_dashboard_update(cmd, client,
                            resource_group_name,
                            name,
                            tags=None,
                            properties_lenses=None,
                            properties_metadata=None):
    properties_lenses = json.loads(properties_lenses) if isinstance(properties_lenses, str) else properties_lenses
    return client.update(resource_group_name=resource_group_name, dashboard_name=name, tags=tags, lenses=properties_lenses, metadata=properties_metadata)


def portal_dashboard_delete(cmd, client,
                            resource_group_name,
                            name):
    return client.delete(resource_group_name=resource_group_name, dashboard_name=name)
