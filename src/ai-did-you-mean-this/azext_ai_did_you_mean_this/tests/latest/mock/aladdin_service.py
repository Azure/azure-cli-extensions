# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import unittest.mock as mock
from contextlib import contextmanager
from functools import wraps
from typing import List

import requests

from azext_ai_did_you_mean_this._suggestion import Suggestion
from azext_ai_did_you_mean_this._suggestion_encoder import SuggestionEncoder
from azext_ai_did_you_mean_this.tests.latest.data._scenario import (
    DEFAULT_REQUEST_SCENARIO,
    RequestScenario,
    Scenario
)


class MockAladdinServiceResponse():
    def __init__(self,
                 suggestions: List[Suggestion],
                 request_scenario: RequestScenario = DEFAULT_REQUEST_SCENARIO):
        super().__init__()
        self._request_scenario = request_scenario
        self._response = requests.Response()
        self._response.status_code = request_scenario.status
        # pylint: disable=protected-access
        self._response._content = bytes(json.dumps(suggestions, cls=SuggestionEncoder), 'utf-8')

    @property
    def response(self) -> requests.Response:
        if self._request_scenario.raises:
            self._request_scenario.raise_exception()
        return self._response

    @staticmethod
    def from_scenario(scenario: Scenario) -> 'MockAladdinServiceResponse':
        return MockAladdinServiceResponse(scenario.suggestions, scenario.request_scenario)


@contextmanager
def mock_aladdin_service_call(scenario: Scenario):
    mock_response = MockAladdinServiceResponse.from_scenario(scenario)

    @wraps(requests.get)
    def get(*_, **__):
        return mock_response.response

    with mock.patch('requests.get', wraps=get):
        yield None
