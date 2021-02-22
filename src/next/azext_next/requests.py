# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import hashlib
import json
from azure.cli.core.azclierror import RecommendationError
from azure.cli.core import telemetry
from azure.cli.core import __version__ as version


# pylint: disable=protected-access
def get_recommend_from_api(command_list, type, top_num=5, error_info=None):  # pylint: disable=unused-argument
    '''query next command from web api'''
    import requests
    url = "https://cli-recommendation.azurewebsites.net/api/RecommendationService"

    user_id = telemetry._get_user_azure_id()  # pylint: disable=protected-access
    hashed_user_id = hashlib.sha256(user_id.encode('utf-8')).hexdigest()
    payload = {
        "command_list": json.dumps(command_list),
        "type": type,
        "top_num": top_num,
        'error_info': error_info,
        'cli_version': version,
        'user_id': hashed_user_id
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
        raise RecommendationError(
            "Failed to connect to '{}' with status code '{}' and reason '{}'".format(
                url, response.status_code, response.reason))

    recommends = []
    if 'data' in response.json():
        recommends = response.json()['data']

    return recommends
