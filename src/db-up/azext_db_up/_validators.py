# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=import-error
import uuid
from six.moves import configparser
from azure.cli.core.commands.validators import get_default_location_from_resource_group
from azure.mgmt.resource.resources.models import ResourceGroup
from knack.log import get_logger
from knack.util import CLIError
from msrestazure.azure_exceptions import CloudError
from msrest.exceptions import ValidationError
from azext_db_up._client_factory import resource_client_factory
from azext_db_up.random_name.generate import generate_username
from azext_db_up.util import create_random_resource_name, get_config_value, set_config_value, remove_config_value

logger = get_logger(__name__)

DEFAULT_LOCATION = 'westus2'
DEFAULT_DATABASE_NAME = 'sampledb'


def db_up_namespace_processor(db_type):
    return lambda cmd, namespace: _process_db_up_namespace(cmd, namespace, db_type=db_type)


def db_down_namespace_processor(db_type):
    return lambda cmd, namespace: _process_db_down_namespace(namespace, db_type=db_type)


# pylint: disable=bare-except
def _process_db_up_namespace(cmd, namespace, db_type=None):
    # populate from cache if existing when no resource group name provided
    resource_client = resource_client_factory(cmd.cli_ctx)
    if namespace.resource_group_name is None:
        _set_value(db_type, namespace, 'resource_group_name', 'group', cache=False)
        try:
            resource_client.resource_groups.get(namespace.resource_group_name)
        except:  # Clear resource group name information when it is invalid
            namespace.resource_group_name = None

    # populate from cache if existing when no location provided
    if namespace.location is None:
        _set_value(db_type, namespace, 'location', 'location', cache=False)
    # generate smart defaults when namespace.location is None
    if _get_value(db_type, namespace, 'location', 'location') is None:
        try:
            get_default_location_from_resource_group(cmd, namespace)
        except (CLIError, ValidationError):
            namespace.location = 'eastus'
    _set_value(db_type, namespace, 'location', 'location', default=namespace.location)

    # When resource group name in namespace is different from what in cache, reset it and create new server name
    if namespace.resource_group_name != get_config_value(db_type, 'group', None):
        set_config_value(db_type, 'group', namespace.resource_group_name)
        if namespace.server_name is None:
            namespace.server_name = create_random_resource_name('server')
            set_config_value(db_type, 'server', namespace.server_name)

    # When no resource group name in namespace and cache, create new resource group with random name
    create_resource_group = True
    if namespace.resource_group_name is None:  # No resource group provided and in cache
        namespace.resource_group_name = create_random_resource_name('group')
    else:
        try:
            resource_client.resource_groups.get(namespace.resource_group_name)
            create_resource_group = False
        except CloudError:  # throw exception when resource group name is invalid
            pass

    if create_resource_group:
        # create new resource group
        params = ResourceGroup(location=namespace.location)
        logger.warning('Creating Resource Group \'%s\'...', namespace.resource_group_name)
        resource_client.resource_groups.create_or_update(namespace.resource_group_name, params)
    _set_value(db_type, namespace, 'resource_group_name', 'group', default=namespace.resource_group_name)

    _set_value(db_type, namespace, 'server_name', 'server', default=create_random_resource_name('server'))
    _set_value(db_type, namespace, 'administrator_login', 'login', default=generate_username())
    if namespace.generate_password:
        namespace.administrator_login_password = str(uuid.uuid4())
    del namespace.generate_password
    _set_value(db_type, namespace, 'database_name', 'database', default=DEFAULT_DATABASE_NAME)


def _process_db_down_namespace(namespace, db_type=None):
    # populate from cache if existing
    if namespace.resource_group_name is None:
        namespace.resource_group_name = _get_value(db_type, namespace, 'resource_group_name', 'group')
        remove_config_value(db_type, 'group')
    if namespace.server_name is None and not namespace.delete_group:
        namespace.server_name = _get_value(db_type, namespace, 'server_name', 'server')
        remove_config_value(db_type, 'server')
        remove_config_value(db_type, 'login')
        remove_config_value(db_type, 'database')
        remove_config_value(db_type, 'location')

    # put resource group info back in config if user does not want to delete it
    if not namespace.delete_group and namespace.resource_group_name:
        _set_value(db_type, namespace, 'resource_group_name', 'group')

    # error handling
    if namespace.delete_group and not namespace.resource_group_name:
        raise CLIError("Please specify the resource group name to delete.")
    if not namespace.delete_group and not namespace.resource_group_name and not namespace.server_name:
        raise CLIError("Please specify the {} server name to delete and its resource group name if you only want to "
                       "delete the specific {} server.".format(db_type, db_type))


def _set_value(db_type, namespace, attribute, option, default=None, cache=True):
    if getattr(namespace, attribute) is None:
        try:
            if get_config_value(db_type, option):
                setattr(namespace, attribute, get_config_value(db_type, option))
            else:
                setattr(namespace, attribute, default)
        except (configparser.NoSectionError, configparser.NoOptionError):
            if default is not None:
                setattr(namespace, attribute, default)
    if cache:
        set_config_value(db_type, option, getattr(namespace, attribute))


def _get_value(db_type, namespace, attribute, option):
    return getattr(namespace, attribute, None) or get_config_value(db_type, option, None)
