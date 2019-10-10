# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# # --------------------------------------------------------------------------------------------
from uuid import uuid4

from knack.log import get_logger
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import ResourceType
from azure.mgmt.resource.resources.models import ResourceGroup

from ._data_store_utils import DataStore
from ._website_utils import Website
from ._cogsvcs_utils import (
    create_cogsvcs_key,
    get_cogsvcs_key
)

logger = get_logger(__name__)

def hack_up(cmd, name, runtime, database, location, ai=None):
    # TODO: Update this to use a default location, or prompt??
    name = name + str(uuid4())[:5]
    # # Create RG
    logger.warning("Creating resource group...")
    create_resource_group(cmd, name, location)

    if ai:
        logger.warning('Starting creation of Cognitive Services keys...')
        create_cogsvcs_key(cmd, name, location)

    logger.warning("Starting database creation job...")
    data_store = DataStore(cmd, database, name, location)
    data_store_poller = data_store.create()

    logger.warning("Starting website creation job...")
    website = Website(cmd, name, location, runtime)
    website.create()

    while True:
        data_store_poller.result(15)
        if data_store_poller.done():
            break

    app_settings = {
        'DATABASE_HOST': data_store.host,
        'DATABASE_NAME': data_store.name,
        'DATABASE_PORT': data_store.port,
        'DATABASE_USER': data_store.admin if data_store.datastore_type != 'mysql' else data_store.admin + '@' + data_store.name,
        'DATABASE_PASSWORD': data_store.password,
    }

    if ai:
        app_settings.update({
            'COGSVCS_KEY': get_cogsvcs_key(cmd, name),
            'COGSVCS_CLIENTURL': 'https://{}.api.cognitive.microsoft.com/'.format(location)
        })

    website.update_settings(app_settings)
    website.finalize_resource_group()

    output = {}

    deployment_info = {
        'Deployment url': website.deployment_url,
        'Git login': website.deployment_user_name,
    }

    if website.deployment_user_password:
        deployment_info.update({'Git password': website.deployment_user_password})
    else:
        deployment_info.update({'Git password info': 'Cannot retrieve password. To change, use `az webapp deployment user set --user-name {}`'.format(website.deployment_user_name)})

    deployment_steps = {
        '1- Create git repository': 'git init',
        '2- Add all code': 'git add .',
        '3- Commit code': 'git commit -m \'Initial commit\'',
        '4- Add remote to git': 'git remote add azure ' + website.deployment_url,
        '5- Deploy to Azure': 'git push azure'
    }

    output.update({'Settings and keys': {
        'Note': 'All values are stored as environmental variables on website',
        'Values': app_settings
    }})
    output.update({'Deployment info': deployment_info})
    output.update({'Deployment steps': deployment_steps})
    output.update({'Website url': website.host_name})

    return output

def create_resource_group(cmd, name, location):
    client = get_mgmt_service_client(
        cmd.cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES)
    params = ResourceGroup(location=location)
    client.resource_groups.create_or_update(name, params)
