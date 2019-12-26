# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument


def list_mixed_reality(cmd, client):
    return client.list()


def check_name_availability_local_mixed_reality_check_name_availability(cmd, client,
                                                                        location):
    body = {}
    return client.check_name_availability_local(location=location, check_name_availability=body)


def create_mixed_reality(cmd, client,
                         resource_group,
                         name,
                         location,
                         tags=None,
                         serial=None):
    body = {}
    body['tags'] = tags  # dictionary
    body['location'] = location  # str
    body['serial'] = serial  # number
    return client.create(resource_group_name=resource_group, spatial_anchors_account_name=name, spatial_anchors_account=body)


def update_mixed_reality(cmd, client,
                         resource_group,
                         name,
                         tags=None,
                         location=None,
                         serial=None):
    body = client.get(resource_group_name=resource_group, spatial_anchors_account_name=name).as_dict()
    if tags is not None:
        body['tags'] = tags  # dictionary
    if location is not None:
        body['location'] = location  # str
    if serial is not None:
        body['serial'] = serial  # number
    return client.create(resource_group_name=resource_group, spatial_anchors_account_name=name, spatial_anchors_account=body)


def delete_mixed_reality(cmd, client,
                         resource_group,
                         name):
    return client.delete(resource_group_name=resource_group, spatial_anchors_account_name=name)


def get_mixed_reality(cmd, client,
                      resource_group,
                      name):
    return client.get(resource_group_name=resource_group, spatial_anchors_account_name=name)


def list_mixed_reality(cmd, client,
                       resource_group):
    if resource_group is not None:
        return client.list_by_resource_group(resource_group_name=resource_group)
    return client.list_by_subscription()


def regenerate_keys_mixed_reality(cmd, client,
                                  resource_group,
                                  name):
    body = {}
    return client.regenerate_keys(resource_group_name=resource_group, spatial_anchors_account_name=name, spatial_anchors_account_key_regenerate=body)


def get_keys_mixed_reality(cmd, client,
                           resource_group,
                           name):
    return client.get_keys(resource_group_name=resource_group, spatial_anchors_account_name=name)
