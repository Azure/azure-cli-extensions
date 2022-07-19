import json

from azure.cli.core import telemetry

from ._clierror import ScenarioSearchError
from .constants import SearchType


def get_search_result_from_api(keyword, type=SearchType.All, top_num=5):
    '''Search related e2e scenarios'''
    import requests
    url = "https://cli-recommendation.azurewebsites.net/api/SearchService"
    payload = {
        "keyword": keyword,
        "type": type,
        "top_num": top_num,
    }

    correlation_id = telemetry._session.correlation_id
    subscription_id = telemetry._get_azure_subscription_id()
    if telemetry.is_telemetry_enabled():
        if correlation_id:
            payload['correlation_id'] = correlation_id
        if subscription_id:
            payload['subscription_id'] = subscription_id

    response = requests.post(url, json.dumps(payload))
    if response.status_code != 200:
        raise ScenarioSearchError(
            "Failed to connect to '{}' with status code '{}' and reason '{}'".format(
                url, response.status_code, response.reason))
    
    results = []
    if 'data' in response.json():
        results = response.json()['data']
    
    print(f'Result len: {len(results)}')
    return results
