# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import json
import requests
from knack.util import CLIError

ARM_TRANSLATOR_URL = 'https://portal2cli.azurewebsites.net/api/v1'


def translate_arm(cmd, template_path, parameters_path, resource_group_name, custom_subscription=None):
    if not os.path.exists(template_path) or not os.path.exists(parameters_path):
        raise CLIError('--template or --parameters file not found')

    with open(template_path, 'r') as fp:
        template_content = fp.read()
    with open(parameters_path, 'r') as fp:
        parameters_content = fp.read()
    if not template_content or not parameters_content:
        raise CLIError('--template or --parameters file is empty')

    if custom_subscription is None:
        from azure.cli.core.commands.client_factory import get_subscription_id
        custom_subscription = get_subscription_id(cmd.cli_ctx)
    try:
        response = requests.post(
            ARM_TRANSLATOR_URL,
            json={
                'resourceGroup': resource_group_name,
                'subscriptionId': custom_subscription,
                'template': json.loads(template_content),
                'parameters': json.loads(parameters_content)
            })
        if response.status_code != 200:
            raise CLIError('The service fail to translate ARM template to CLI scripts. \n{}'.format(response.text))
        scripts = response.json()
        for script in scripts:
            print('{}\n\n'.format(script))
    except Exception as e:
        raise CLIError('Meet exception while call translate service, please try a few minutes later.\n{}', str(e))

