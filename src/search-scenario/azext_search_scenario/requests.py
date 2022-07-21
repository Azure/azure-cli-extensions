# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import json

from ._clierror import ScenarioSearchError
from .constants import SearchType, SEARCH_SERVICE_URL


def get_search_result_from_api(keyword, typ=SearchType.All, top_num=5):
    '''Search related e2e scenarios'''
    import requests

    payload = {
        "keyword": keyword,
        "type": typ,
        "top_num": top_num,
    }

    response = requests.post(SEARCH_SERVICE_URL, json.dumps(payload))
    if response.status_code != 200:
        raise ScenarioSearchError(
            f"Failed to connect to '{SEARCH_SERVICE_URL}' with status code "
            f"'{response.status_code}' and reason '{response.reason}'")

    results = []
    if 'data' in response.json():
        results = response.json()['data']

    return results
