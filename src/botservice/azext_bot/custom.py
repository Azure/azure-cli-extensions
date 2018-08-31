# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from knack.log import get_logger
from azure.mgmt.botservice.models import Bot, BotProperties, Sku
from azure.cli.command_modules.botservice.custom import create_app, provisionConvergedApp
from azure.cli.core._profile import Profile  # pylint: disable=unused-import

logger = get_logger(__name__)


def create(cmd, client, resource_group_name, resource_name, kind, description=None, display_name=None,
           endpoint=None, msa_app_id=None, password=None, tags=None, storageAccountName=None,
           location='Central US', sku_name='F0', appInsightsLocation='South Central US',
           language='Csharp', version='v3'):
    display_name = display_name or resource_name
    kind = kind.lower()

    if not msa_app_id:
        msa_app_id, password = provisionConvergedApp(resource_name)
        logger.warning('obtained msa app id and password. Provisioning bot now.')

    if kind == 'registration':
        kind = 'bot'
        if not endpoint or not msa_app_id:
            raise CLIError('Endpoint and msa app id are required for creating a registration bot')
        parameters = Bot(
            location='global',
            sku=Sku(name=sku_name),
            kind=kind,
            tags=tags,
            properties=BotProperties(
                display_name=display_name,
                description=description,
                endpoint=endpoint,
                msa_app_id=msa_app_id
            )
        )
        return client.bots.create(
            resource_group_name=resource_group_name,
            resource_name=resource_name,
            parameters=parameters
        )
    if kind in ('webapp', 'function'):
        return create_app(cmd, client, resource_group_name, resource_name, description, kind, msa_app_id, password,
                          storageAccountName, location, sku_name, appInsightsLocation, language, version)
    else:
        raise CLIError('Invalid Bot Parameter : Kind')
