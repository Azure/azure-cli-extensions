import random
import json
import requests

from knack.log import get_logger
logger = get_logger(__name__)

wait_messages = ['Ok, let me find an answer to that question for you.',
                 'I\'m working on finding the right anwser for you.', 'Let me see if I answer that for you.']

def processquery(query):
    # print(cmd.__dict__)
    print(random.choice(wait_messages))
    logger.warn('Please wait...')
    print(process_answer(query))


def process_answer(query):
    answer_list = call_aladdin_service(query)
    if answer_list:
        print(answer_list[0]['snippet'],
              "\nFor more information please see:", answer_list[0]['link'])
    else:
        print("Not 100% sure. But, here are some information I was able to gather for you: ")
        # Bing search result


def call_aladdin_service(query):
    service_input = {
        'paragraphText': "",
        'currentPageUrl': "",
        'query': "ALADDIN-CLI:"+query,
        'context': ""
    }

    api_url = 'https://aladdinservice-staging.azurewebsites.net/api/aladdin/generateCards'
    headers = {'Content-Type': 'application/json'}

    response = requests.post(api_url, headers=headers, json=service_input)

    if response.status_code == 200:
        answers = json.loads(response.content)
        return answers

    print('[?] Unexpected Error: [HTTP {0}]: Content: {1}'.format(response.status_code, response.content))
    return None
