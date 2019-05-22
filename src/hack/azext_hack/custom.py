# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# # --------------------------------------------------------------------------------------------
from knack.log import get_logger


from .utils import(
    create_resource_group,
    create_database,
    create_website
)

logger = get_logger(__name__)

def hack_up(cmd, name):
    location = 'westus'
    # Create RG
    logger.warning("Creating resource group")
    create_resource_group(cmd, name, location)
    logger.warning("Created resource group")
    # Create SQL server and database
    logger.warning("Starting database creation job...")
    database_poller = create_database(cmd, name, location)

    # Create git deployment account or use existing

    # Create app service plan and website
    logger.warning("Starting website creation job...")
    web_app = create_website(cmd, name, location)

    while not database_poller.done():
        pass
    logger.warning('Done!!!')

    # Add app setting with connection string
    # Display information
    return 'Done!'

def hack_down(cmd, name, dryrun=False, confirm=False):
    # confirm
    pass
