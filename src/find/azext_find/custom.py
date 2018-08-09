# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import random
import json
import requests

from knack.log import get_logger
logger = get_logger(__name__)

wait_messages = ['Ok, let me find an answer to that question for you.',
                 'I\'m working on finding the right answer for you.', 'Let me see if I answer that for you.']


def process_query(question):
    print(random.choice(wait_messages))
    response = call_aladdin_service(question)

    if response.status_code != 200:
        logger.error('[?] Unexpected Error: [HTTP {0}]: Content: {1}'.format(response.status_code, response.content))
    else:
        answer_list = json.loads(response.content)
        num_results_to_show = 1
        if answer_list:
            if answer_list[0]['source'] == 'bing':
                print("Here are some information I was able to gather for you: ")
                num_results_to_show = 3
            for i in range(num_results_to_show):
                print(answer_list[i]['title'].strip())
                print("- - - - - - - - - - - - - - - - - - - - - ")
                print(answer_list[i]['snippet'].strip())
                print("More info: ", answer_list[i]['link'])
                if i + 1 < num_results_to_show:
                    print("=========================================")


def call_aladdin_service(query):
    service_input = {
        'paragraphText': "",
        'currentPageUrl': "",
        'query': "ALADDIN-CLI:" + query,
        'context': ""
    }

    api_url = 'https://aladdinservice-staging.azurewebsites.net/api/aladdin/generateCards'
    headers = {'Content-Type': 'application/json'}

    response = requests.post(api_url, headers=headers, json=service_input)

    return response
