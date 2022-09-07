# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import json

from ._clierror import SearchScenarioError
from .constants import MatchRule, SearchScope, SEARCH_SERVICE_URL


def search_online(keyword, scope=SearchScope.All, match_rule=MatchRule.All, top=5):
    '''Search related e2e scenarios'''
    import requests

    payload = {
        "keyword": keyword,
        "scope": scope,
        "match_rule": match_rule,
        "top_num": top,
    }

    response = requests.post(SEARCH_SERVICE_URL, json.dumps(payload))
    if response.status_code != 200:
        raise SearchScenarioError(
            f"Failed to connect to '{SEARCH_SERVICE_URL}' with status code "
            f"'{response.status_code}' and reason '{response.reason}'")

    results = []
    if 'data' in response.json():
        results = response.json()['data']

    return results
