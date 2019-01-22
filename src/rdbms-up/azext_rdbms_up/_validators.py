# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import uuid
from six.moves import configparser
from azure.cli.core.commands.validators import get_default_location_from_resource_group
from azure.mgmt.resource.resources.models import ResourceGroup
from azext_rdbms_up._client_factory import resource_client_factory
from azext_rdbms_up.random_name.generate import generate_username
from azext_rdbms_up.util import create_random_resource_name, get_config_value, set_config_value
from knack.log import get_logger

logger = get_logger(__name__)

DEFAULT_LOCATION = 'westus2'
DEFAULT_DATABASE_NAME = 'sampledb'


def process_mysql_namespace(cmd, namespace):
    # Create smart defaults
    if _get_value(namespace, 'location', 'location') is None:
        if namespace.resource_group_name is None:
            namespace.location = 'westus2'
        else:
            get_default_location_from_resource_group(cmd, namespace)
    _set_value(namespace, 'location', 'location', namespace.location)

    if _get_value(namespace, 'resource_group_name', 'group') is None:
        # create new resource group
        namespace.resource_group_name = create_random_resource_name('group')
        resource_client = resource_client_factory(cmd.cli_ctx)
        params = ResourceGroup(location=namespace.location)
        logger.warning('Creating Resource Group \'%s\' ...', namespace.resource_group_name)
        resource_client.resource_groups.create_or_update(namespace.resource_group_name, params)
    _set_value(namespace, 'resource_group_name', 'group', namespace.resource_group_name)

    _set_value(namespace, 'server_name', 'server', create_random_resource_name('server'))
    _set_value(namespace, 'administrator_login', 'login', generate_username())
    if namespace.generate_password:
        namespace.administrator_login_password = str(uuid.uuid4())
    del namespace.generate_password
    _set_value(namespace, 'database_name', 'database', DEFAULT_DATABASE_NAME)


def _set_value(namespace, attribute, option, default, cache=True):
    if getattr(namespace, attribute) is None:
        try:
            setattr(namespace, attribute, get_config_value(option))
        except (configparser.NoSectionError, configparser.NoOptionError):
            setattr(namespace, attribute, default)
    if cache:
        set_config_value(option, getattr(namespace, attribute))


def _get_value(namespace, attribute, option):
    return getattr(namespace, attribute, None) or get_config_value(option, None)
