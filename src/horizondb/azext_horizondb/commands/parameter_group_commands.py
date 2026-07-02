# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long, too-many-locals

from azure.cli.core.util import sdk_no_wait, user_confirmation


def horizondb_parameter_group_create(client, resource_group_name, parameter_group_name, location,
                                     parameters=None, description=None, pg_version=None,
                                     apply_immediately=None, tags=None, no_wait=False):
    from azext_horizondb.vendored_sdks.models import (
        HorizonDbParameterGroup,
        HorizonDbParameterGroupProperties,
    )

    properties = HorizonDbParameterGroupProperties(
        parameters=parameters,
        description=description,
        pg_version=pg_version,
        apply_immediately=apply_immediately,
    )

    resource = HorizonDbParameterGroup(
        location=location,
        tags=tags,
        properties=properties,
    )

    return sdk_no_wait(no_wait, client.begin_create_or_update,
                       resource_group_name=resource_group_name,
                       parameter_group_name=parameter_group_name,
                       resource=resource)


def horizondb_parameter_group_delete(client, resource_group_name, parameter_group_name, no_wait=False, yes=False):
    if not yes:
        user_confirmation(
            "Are you sure you want to delete the parameter group '{0}' in resource group '{1}'".format(
                parameter_group_name, resource_group_name), yes=yes)
    return sdk_no_wait(no_wait, client.begin_delete,
                       resource_group_name=resource_group_name,
                       parameter_group_name=parameter_group_name)


def horizondb_parameter_group_list(client, resource_group_name=None):
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name=resource_group_name)
    return client.list_by_subscription()
