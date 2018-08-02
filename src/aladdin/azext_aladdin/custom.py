import requests
import json

from knack.log import get_logger
logger = get_logger(__name__)
import random

wait_messages = ['Ok, let me find an answer to that question for you.', 'I\'m working on finding the right anwser for you.', 'Let me see if I answer that for you.']


def processquery(query):
    #print(cmd.__dict__)
    print(random.choice(wait_messages))
    logger.warn('Please wait...')
    print(process_answer(query))

def process_answer(query):
    answer_list = call_aladdin_service(query)
    if((len(answer_list) > 0) & (answer_list is not None)):
        print(answer_list[0]['snippet'], "\nFor more information please see:", answer_list[0]['link'])
    else: 
        print("I'm not enitirely sure how to help with this. But, here are some information I was able to gather for you: ")
        #Bing search result


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

    if response.status_code >= 500:
        #print('[!] [{0}] Server Error'.format(response.status_code))
        return None
    elif response.status_code == 404:
        #print('[!] [{0}] URL not found: [{1}]'.format(response.status_code,api_url))
        return None
    elif response.status_code == 401:
        #print('[!] [{0}] Authentication Failed'.format(response.status_code))
        return None
    elif response.status_code >= 400:
        #print('[!] [{0}] Bad Request'.format(response.status_code))
        #print(response.content )
        return None
    elif response.status_code >= 300:
        #print('[!] [{0}] Unexpected redirect.'.format(response.status_code))
        return None
    elif response.status_code == 200:
        answers = json.loads(response.content)
        return answers
    else:
        #print('[?] Unexpected Error: [HTTP {0}]: Content: {1}'.format(response.status_code, response.content))
        return None