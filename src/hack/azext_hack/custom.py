# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from .utils import(
    create_resource_group
)
from knack.log import get_logger
logger = get_logger(__name__)

def hack_up(cmd, name, location='westus'):
    # Create RG
    logger.warning("Creating resource group")
    create_resource_group(cmd, name, location)
    # Create database
    # Create git deployment account or use existing
    # Create app service plan w/ local git deploy
    # Add app setting with connection string
    # Display information

def hack_down(cmd, name, dryrun=False, confirm=False):
    # confirm
    pass
