# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# # --------------------------------------------------------------------------------------------
from uuid import uuid4
from knack.log import get_logger

from .utils import (
    create_resource_group,
    create_database,
    create_website,
    set_website_settings,
    create_cogsvcs_key
)

logger = get_logger(__name__)


def hack_up(cmd, name, runtime, database, ai=None):
    location = 'westus'
    database_admin = name + '_user'
    database_password = uuid4()
    output = {}

    # Create RG
    logger.warning("Creating resource group")
    create_resource_group(cmd, name, location)
    logger.warning("Created resource group")

    # Create CogSvcs key
    # TODO: Make this async and move it to the top
    if ai:
        logger.warning('Starting creation of Cognitive Services keys...')
        create_cogsvcs_key(cmd, name, location)

    # Create SQL server and database
    logger.warning("Starting database creation job...")
    database_poller = create_database(cmd, database, name, location, database_admin, database_password)
    # Create app service plan and website
    logger.warning("Starting website creation job...")
    output = create_website(cmd, name, runtime)
    # Database takes a while. Wait at the end for it to complete
    while True:
        database_poller.result(15)
        if database_poller.done():
            break

    output['settings'] = set_website_settings(cmd, name, database, database_admin, database_password, ai)
    if output['deployment_password'] == '***':
        logger.warning('Deployment user was already created. To change password use `az webapp deployment user set`')
    else:
        logger.warning('Created password for deployment user. To change use `az webapp deployment user set`')
    return output
