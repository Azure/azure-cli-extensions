# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import json
import requests
from urllib.parse import urlparse
from azure.cli.core.azclierror import InvalidArgumentValueError, AzureInternalError

ARM_TRANSLATOR_URL = 'https://portal2cli.azurewebsites.net/api/v1'


def _is_url(url):
    return urlparse(url).scheme != ""


def _read_json(path):
    content = None
    try:
        if _is_url(path):
            content = requests.get(path).text
        else:
            with open(path, 'r') as fp:
                content = fp.read()
        if content:
            content = json.loads(content)
    except Exception as e:
        pass
    return content


def translate_arm(cmd, template_path, parameters_path, resource_group_name, target_subscription=None):
    template_content = _read_json(template_path)
    if not template_content:
        raise InvalidArgumentValueError('Please make sure --template is a valid template file or url')

    parameters_content = _read_json(parameters_path)
    if not parameters_content:
        raise InvalidArgumentValueError('Please make sure --parameters is a valid parameters file or url')

    if target_subscription is None:
        from azure.cli.core.commands.client_factory import get_subscription_id
        target_subscription = get_subscription_id(cmd.cli_ctx)
    try:
        response = requests.post(
            ARM_TRANSLATOR_URL,
            json={
                'resourceGroup': resource_group_name,
                'subscriptionId': target_subscription,
                'template': template_content,
                'parameters': parameters_content
            })
        if response.status_code != 200:
            raise AzureInternalError(
                'The service fail to translate ARM template to CLI scripts. \n{}'.format(response.text))
        scripts = response.json()
        for script in scripts:
            print('{}\n\n'.format(script))
    except Exception as e:
        raise AzureInternalError(
            'Meet exception while call translate service, please try a few minutes later.\n' + str(e))
