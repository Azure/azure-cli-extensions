# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# # --------------------------------------------------------------------------------------------
from azure.cli.command_modules.sql._util import (
    get_sql_management_client
)
from azure.cli.command_modules.sql.custom import (
    server_create
)
from azure.cli.core.util import (
    sdk_no_wait,
)

from knack.log import get_logger


from .utils import(
    create_resource_group
)

logger = get_logger(__name__)

def hack_up(cmd, name):
    location = 'westus'
    # Create RG
    logger.warning("Creating resource group")
    create_resource_group(cmd, name, location)
    logger.warning("Created resource group")
    # Create database
    logger.warning("Creating SQL Server")
    sql_client = get_sql_management_client(cmd.cli_ctx).servers
    sql_parameters = {
        'location': location, # "self.region" is 'west-us' by default
        'version': '12.0',
        'administrator_login': 'mysecretname',
        'administrator_login_password': 'HusH_Sec4et'
    }

    poller = server_create(sql_client, name, name, **sql_parameters)
    if not poller.done():
        logger.warning('Running operation...')
    while not poller.done():
        pass
    # sql_client.create_or_update(resource_group_name=name,
    #                             server_name=name,
    #                             parameters=sql_parameters)
    logger.warning("Created SQL Server")
    # Create git deployment account or use existing
    # Create app service plan w/ local git deploy
    # Add app setting with connection string
    # Display information
    return 'Done!'


def hack_down(cmd, name, dryrun=False, confirm=False):
    # confirm
    pass
