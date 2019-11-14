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
from azext_db_up.util import create_random_resource_name, get_config_value, set_config_value

logger = get_logger(__name__)

DEFAULT_LOCATION = 'westus2'
DEFAULT_DATABASE_NAME = 'sampledb'


def db_up_namespace_processor(db_type):
    return lambda cmd, namespace: _process_db_up_namespace(cmd, namespace, db_type=db_type)


def db_down_namespace_processor(db_type):
    return lambda cmd, namespace: _process_db_down_namespace(namespace, db_type=db_type)


def _process_db_up_namespace(cmd, namespace, db_type=None):
    # populate from cache if existing
    _set_value(db_type, namespace, 'location', 'location', cache=False)
    _set_value(db_type, namespace, 'resource_group_name', 'group', cache=False)

    # generate smart defaults
    if _get_value(db_type, namespace, 'location', 'location') is None:
        try:
            get_default_location_from_resource_group(cmd, namespace)
        except (CLIError, ValidationError):
            namespace.location = 'westus2'
    _set_value(db_type, namespace, 'location', 'location', namespace.location)

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
        logger.warning('Creating Resource Group \'%s\'...', namespace.resource_group_name)
        resource_client.resource_groups.create_or_update(namespace.resource_group_name, params)
    _set_value(db_type, namespace, 'resource_group_name', 'group', namespace.resource_group_name)

    _set_value(db_type, namespace, 'server_name', 'server', create_random_resource_name('server'))
    _set_value(db_type, namespace, 'administrator_login', 'login', generate_username())
    if namespace.generate_password:
        namespace.administrator_login_password = str(uuid.uuid4())
    del namespace.generate_password
    _set_value(db_type, namespace, 'database_name', 'database', DEFAULT_DATABASE_NAME)


def _process_db_down_namespace(namespace, db_type=None):
    # populate from cache if existing
    _set_value(db_type, namespace, 'resource_group_name', 'group', cache=False)
    _set_value(db_type, namespace, 'server_name', 'server', cache=False)

    # put resource group info back in config if user does not want to delete it
    if not namespace.delete_group:
        _set_value(db_type, namespace, 'resource_group_name', 'group')


def _set_value(db_type, namespace, attribute, option, default=None, cache=True):
    if getattr(namespace, attribute) is None:
        try:
            setattr(namespace, attribute, get_config_value(db_type, option))
        except (configparser.NoSectionError, configparser.NoOptionError):
            if default is not None:
                setattr(namespace, attribute, default)
    if cache:
        set_config_value(db_type, option, getattr(namespace, attribute))


def _get_value(db_type, namespace, attribute, option):
    return getattr(namespace, attribute, None) or get_config_value(db_type, option, None)
