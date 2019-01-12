# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import uuid
from azure.cli.core.commands.validators import get_default_location_from_resource_group
from azure.mgmt.resource.resources.models import ResourceGroup
from azext_rdbms_up._client_factory import resource_client_factory
from azext_rdbms_up.random_name.generate import generate_username
from azext_rdbms_up.util import create_random_resource_name
from knack.log import get_logger

logger = get_logger(__name__)


def process_mysql_namespace(cmd, namespace):
    # Create smart defaults
    if namespace.location is None:
        if namespace.resource_group_name is None:
            namespace.location = 'westus2'
        else:
            get_default_location_from_resource_group(cmd, namespace)

    if namespace.resource_group_name is None:
        # create new resource group
        namespace.resource_group_name = create_random_resource_name('group')
        resource_client = resource_client_factory(cmd.cli_ctx)
        params = ResourceGroup(location=namespace.location)
        logger.warning('Creating Resource Group \'%s\' ...', namespace.resource_group_name)
        resource_client.resource_groups.create_or_update(namespace.resource_group_name, params)

    if namespace.server_name is None:
        namespace.server_name = create_random_resource_name('server')

    if namespace.administrator_login is None:
        namespace.administrator_login = generate_username()

    if namespace.administrator_login_password is None:
        namespace.administrator_login_password = str(uuid.uuid4())
