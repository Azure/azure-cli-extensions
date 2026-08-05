# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument, line-too-long, import-outside-toplevel, raise-missing-from
import random
from knack.log import get_logger
from azure.cli.core.util import CLIError
from azure.core.exceptions import HttpResponseError
from azure.mgmt.resource.resources.models import ResourceGroup
from .._client_factory import resource_client_factory

logger = get_logger(__name__)

DEFAULT_LOCATION_PG = 'canadacentral'


def create_random_resource_name(prefix='azure', length=15):
    append_length = length - len(prefix)
    digits = [str(random.randrange(10)) for i in range(append_length)]
    return prefix + ''.join(digits)


# pylint: disable=protected-access
def _check_resource_group_existence(cmd, resource_group_name, resource_client=None):
    if resource_client is None:
        resource_client = resource_client_factory(cmd.cli_ctx)

    exists = False

    try:
        exists = resource_client.resource_groups.check_existence(resource_group_name)
    except HttpResponseError as e:
        if e.status_code == 403:
            raise CLIError("You don't have authorization to perform action 'Microsoft.Resources/subscriptions/resourceGroups/read' over scope '/subscriptions/{}/resourceGroups/{}'.".format(resource_client._config.subscription_id, resource_group_name))

    return exists


def _create_resource_group(cmd, location, resource_group_name):
    if resource_group_name is None:
        resource_group_name = create_random_resource_name('group')
    params = ResourceGroup(location=location)
    resource_client = resource_client_factory(cmd.cli_ctx)
    logger.warning('Creating Resource Group \'%s\'...', resource_group_name)
    resource_client.resource_groups.create_or_update(resource_group_name, params)
    return resource_group_name


def check_resource_group(resource_group_name):
    # check if rg is already null originally
    if not resource_group_name:
        return False

    # replace single and double quotes with empty string
    resource_group_name = resource_group_name.replace("'", '')
    resource_group_name = resource_group_name.replace('"', '')

    # check if rg is empty after removing quotes
    if not resource_group_name:
        return False
    return True


def generate_missing_cluster_parameters(cmd, resource_group_name, cluster_name, location):
    # If resource group is there in local context, check for its existence.
    if resource_group_name is not None:
        logger.warning('Checking the existence of the resource group \'%s\'...', resource_group_name)
        resource_group_exists = _check_resource_group_existence(cmd, resource_group_name)
        logger.warning('Resource group \'%s\' exists ? : %s ', resource_group_name, resource_group_exists)
    else:
        resource_group_exists = False

    # set location to be same as RG's if not specified
    if not resource_group_exists:
        if not location:
            location = DEFAULT_LOCATION_PG
        resource_group_name = _create_resource_group(cmd, location, resource_group_name)
    else:
        resource_group_client = resource_client_factory(cmd.cli_ctx).resource_groups
        resource_group = resource_group_client.get(resource_group_name=resource_group_name)
        if not location:
            location = resource_group.location

    # If clustername is not passed, always create a new cluster - even if it is stored in the local context
    if cluster_name is None:
        cluster_name = create_random_resource_name('cluster')

    return resource_group_name, cluster_name.lower(), location
