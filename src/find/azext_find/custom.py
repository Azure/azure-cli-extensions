# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import random
import json
import re
import requests


from azure.cli.core import telemetry as telemetry_core
from knack.prompting import prompt
from knack.log import get_logger
logger = get_logger(__name__)

WAIT_MESSAGE = ['I\'m an AI bot (learn more: aka.ms/azref); Let me see if I can help you...']

EXTENSION_NAME = 'find'
ALIAS_EXTENSION_PREFIX = 'Context.Default.Extension.Find.'

def process_query(cli_command):
    print(random.choice(WAIT_MESSAGE))
    response = call_aladdin_service(cli_command)

    if response.status_code != 200:
        logger.error('[?] Unexpected Error: [HTTP {0}]: Content: {1}'.format(response.status_code, response.content))
    else:
        answer_list = json.loads(response.content)
        if (not answer_list or answer_list[0]['source'] == 'bing'):
            logger.warning("Sorry I am not recognizing [" + cli_command + "] as an Azure CLI command. "
                           "\nTry typing the beginning of a command e.g. 'az vm'.")
        else:
            print("Here are the most common ways to use [" + cli_command + "]: \n")
            num_results_to_show = min(3, len(answer_list))
            for i in range(num_results_to_show):
                current_title = answer_list[i]['title'].strip()
                current_snippet = answer_list[i]['snippet'].strip()
                if current_title.startswith("az "):
                    current_title, current_snippet = current_snippet, current_title
                    current_title = current_title.split('\r\n')[0]
                elif '```azurecli\r\n' in current_snippet:
                    start_index = current_snippet.index('```azurecli\r\n') + len('```azurecli\r\n')
                    current_snippet = current_snippet[start_index:]
                current_snippet = current_snippet.replace('```', '').replace(current_title, '').strip()
                current_snippet = re.sub(r'\[.*\]', '', current_snippet).strip()
                print('\033[1m' + current_title + '\033[0m')
                print(current_snippet)

                print("")
            feedback = prompt("[Enter to close. Press + or - to give feedback]:")
            properties = {}
            set_custom_properties(properties, 'Feedback', feedback)
            telemetry_core.add_extension_event(EXTENSION_NAME, properties)

def set_custom_properties(prop, name, value):
    if name and value is not None:
        # 10 characters limit for strings
        prop['{}{}'.format(ALIAS_EXTENSION_PREFIX, name)] = value[:10] if isinstance(value, str) else value

def call_aladdin_service(query):
    context = {
        'session_id': telemetry_core._session._get_base_properties()['Reserved.SessionId'],  # pylint: disable=protected-access
        'subscription_id': telemetry_core._get_azure_subscription_id(),  # pylint: disable=protected-access
        'client_request_id': telemetry_core._session.application.data['headers']['x-ms-client-request-id'],  # pylint: disable=protected-access
        'installation_id': telemetry_core._get_installation_id()  # pylint: disable=protected-access
    }

    if (query and query.startswith("az ")):
        query = '"' + query + '"'

    service_input = {
        'paragraphText': "<div id='dummyHeader'></div>",
        'currentPageUrl': "",
        'query': "ALADDIN-CLI:" + query,
        'context': context
    }

    api_url = 'https://aladdinservice-staging.azurewebsites.net/api/aladdin/generateCards'
    headers = {'Content-Type': 'application/json'}

    response = requests.post(api_url, headers=headers, json=service_input)

    return response
