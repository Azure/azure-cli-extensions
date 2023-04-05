# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import json

from ._clierror import ScenarioGuideError
from .constants import MatchRule, SearchScope, SEARCH_SERVICE_URL


def search_online(keyword, scope=SearchScope.All, match_rule=MatchRule.All, top=5):
    """Search related e2e scenarios"""
    import requests

    payload = {
        "keyword": keyword,
        "scope": scope,
        "match_rule": match_rule,
        "top_num": top,
    }
    try:
        response = requests.post(SEARCH_SERVICE_URL, json.dumps(payload))
        response.raise_for_status()
    except requests.ConnectionError as e:
        raise ScenarioGuideError(f'Network Error: {e}') from e
    except requests.exceptions.HTTPError as e:
        raise ScenarioGuideError(f'{e}') from e
    except requests.RequestException as e:
        raise ScenarioGuideError(f'Request Error: {e}') from e

    results = []
    if 'data' in response.json():
        results = response.json()['data']

    return results
