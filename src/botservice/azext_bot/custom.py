# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import requests

from knack.util import CLIError
from knack.log import get_logger
from azure.cli.command_modules.botservice.bot_publish_prep import BotPublishPrep
from azure.cli.command_modules.botservice.custom import publish_app as publish_appv3
from azure.cli.command_modules.botservice.http_response_validator import HttpResponseValidator
from azure.cli.command_modules.botservice.kudu_client import KuduClient


logger = get_logger(__name__)


def __install_node_dependencies(kudu_client):
    """Installs Node.js dependencies at `site/wwwroot/` for Node.js bots.

    This method is only called when the detected bot is a Node.js bot.

    :return: Dictionary with results of the HTTP Kudu request
    """
    if not kudu_client._KuduClient__initialized:  # pylint:disable=protected-access
        kudu_client._KuduClient__initialize()  # pylint:disable=protected-access

    payload = {
        'command': 'npm install',
        'dir': r'site\wwwroot'
    }
    response = requests.post(kudu_client._KuduClient__scm_url + '/api/command', data=json.dumps(payload),  # pylint:disable=protected-access
                             headers=kudu_client._KuduClient__get_application_json_headers())   # pylint:disable=protected-access
    HttpResponseValidator.check_response_status(response)
    return response.json()


def publish_app(cmd, client, resource_group_name, resource_name, code_dir=None, proj_name=None, version='v3'):
    """Publish local bot code to Azure.

    This method is directly called via "bot publish"

    :param cmd:
    :param client:
    :param resource_group_name:
    :param resource_name:
    :param code_dir:
    :param proj_name:
    :param version:
    :return:
    """
    if version == 'v3':
        return publish_appv3(cmd, client, resource_group_name, resource_name, code_dir)

    # Get the bot information and ensure it's not only a registration bot.
    bot = client.bots.get(
        resource_group_name=resource_group_name,
        resource_name=resource_name
    )
    if bot.kind == 'bot':
        raise CLIError('Bot kind is \'bot\', meaning it is a registration bot. '
                       'Source publish is not supported for registration only bots.')

    # If the user does not pass in a path to the local bot project, get the current working directory.
    if not code_dir:
        code_dir = os.getcwd()

        logger.info('Parameter --code-dir not provided, defaulting to current working directory, %s. '
                    'For more information, run \'az bot publish -h\'', code_dir)

    if not os.path.isdir(code_dir):
        raise CLIError('The path %s is not a valid directory. '
                       'Please supply a valid directory path containing your source code.' % code_dir)

    # Ensure that the directory contains appropriate post deploy scripts folder
    if 'PostDeployScripts' not in os.listdir(code_dir):
        BotPublishPrep.prepare_publish_v4(logger, code_dir, proj_name)

    logger.info('Creating upload zip file.')
    zip_filepath = BotPublishPrep.create_upload_zip(logger, code_dir, include_node_modules=False)
    logger.info('Zip file path created, at %s.', zip_filepath)

    kudu_client = KuduClient(cmd, resource_group_name, resource_name, bot)
    output = kudu_client.publish(zip_filepath)
    logger.info('Bot source published. Preparing bot application to run the new source.')
    os.remove('upload.zip')
    if os.path.exists(os.path.join('.', 'package.json')):
        logger.info('Detected language javascript. Installing node dependencies in remote bot.')
        __install_node_dependencies(kudu_client)

    if output.get('active'):
        logger.info('Deployment successful!')

    if not output.get('active'):
        scm_url = output.get('url')
        deployment_id = output.get('id')
        # Instead of replacing "latest", which would could be in the bot name, we replace "deployments/latest"
        deployment_url = scm_url.replace('deployments/latest', 'deployments/%s' % deployment_id)
        logger.error('Deployment failed. To find out more information about this deployment, please visit %s.'
                     % deployment_url)

    return output
