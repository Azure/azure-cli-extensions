# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines

import json
from knack.util import CLIError


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
                            input_path,
                            tags=None):
    properties_lenses, properties_metadata = parse_json(input_path)
    return client.create_or_update(resource_group_name=resource_group_name, dashboard_name=name, location=location, tags=tags, lenses=properties_lenses, metadata=properties_metadata)


def portal_dashboard_update(cmd, client,
                            resource_group_name,
                            name,
                            input_path):
    properties_lenses, properties_metadata = parse_json(input_path)
    return client.update(resource_group_name=resource_group_name, dashboard_name=name, lenses=properties_lenses, metadata=properties_metadata)


def portal_dashboard_delete(cmd, client,
                            resource_group_name,
                            name):
    return client.delete(resource_group_name=resource_group_name, dashboard_name=name)


def parse_json(input_path):
    try:
        with open(input_path) as json_file:
            try:
                properties = json.load(json_file)
            except json.decoder.JSONDecodeError as ex:
                raise CLIError('JSON decode error for {}: {}'.format(json_file, str(ex)))
            if 'lenses' not in properties:
                raise CLIError(str(json_file) + " does not contain the property 'lenses'")
            properties_lenses = properties['lenses']
            if 'metadata' not in properties:
                raise CLIError(str(json_file) + " does not contain the property 'metadata'")
            properties_metadata = properties['metadata']
            return properties_lenses, properties_metadata
    except FileNotFoundError as ex:
        raise CLIError('File not Found: {}'.format(str(ex)))
