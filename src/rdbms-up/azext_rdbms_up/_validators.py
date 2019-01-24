# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=import-error
import uuid
from six.moves import configparser
from azure.cli.core.commands.validators import get_default_location_from_resource_group
from azure.mgmt.resource.resources.models import ResourceGroup
from azext_rdbms_up._client_factory import resource_client_factory
from azext_rdbms_up.random_name.generate import generate_username
from azext_rdbms_up.util import create_random_resource_name, get_config_value, set_config_value
from knack.log import get_logger
from knack.util import CLIError
from msrestazure.azure_exceptions import CloudError
from msrest.exceptions import ValidationError

logger = get_logger(__name__)

DEFAULT_LOCATION = 'westus2'
DEFAULT_DATABASE_NAME = 'sampledb'


def process_mysql_namespace(cmd, namespace):
    # populate from cache if existing
    _set_value(namespace, 'location', 'location', cache=False)
    _set_value(namespace, 'resource_group_name', 'group', cache=False)

    # generate smart defaults
    if _get_value(namespace, 'location', 'location') is None:
        try:
            get_default_location_from_resource_group(cmd, namespace)
        except (CLIError, ValidationError):
            namespace.location = 'westus2'
    _set_value(namespace, 'location', 'location', namespace.location)

    create_resource_group = True
    resource_client = resource_client_factory(cmd.cli_ctx)
    if namespace.resource_group_name is None:
        namespace.resource_group_name = create_random_resource_name('group')
    else:
        try:
            resource_client.resource_groups.get(namespace.resource_group_name)
            create_resource_group = False
        except CloudError:
            pass

    if create_resource_group:
        # create new resource group
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


def _set_value(namespace, attribute, option, default=None, cache=True):
    if getattr(namespace, attribute) is None:
        try:
            setattr(namespace, attribute, get_config_value(option))
        except (configparser.NoSectionError, configparser.NoOptionError):
            if default is not None:
                setattr(namespace, attribute, default)
    if cache:
        set_config_value(option, getattr(namespace, attribute))


def _get_value(namespace, attribute, option):
    return getattr(namespace, attribute, None) or get_config_value(option, None)
