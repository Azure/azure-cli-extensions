# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import json
import unittest.mock as mock
from enum import Enum, auto
from http import HTTPStatus
from collections import namedtuple
from contextlib import contextmanager

import requests

from azext_ai_did_you_mean_this.failure_recovery_recommendation import FailureRecoveryRecommendation

# mock service call context attributes
MOCK_UUID = '00000000-0000-0000-0000-000000000000'
MOCK_VERSION = '2.4.0'

# mock recommendation data constants
MOCK_MODEL_DIR = 'model'
MOCK_RECOMMENDATION_MODEL_FILENAME = 'recommendations.json'


RecommendationData = namedtuple('RecommendationData', ['recommendations', 'arguments', 'user_fault_type', 'extension'])


class UserFaultType(Enum):
    MISSING_REQUIRED_SUBCOMMAND = auto()
    NOT_IN_A_COMMAND_GROUP = auto()
    EXPECTED_AT_LEAST_ONE_ARGUMENT = auto()
    UNRECOGNIZED_ARGUMENTS = auto()
    INVALID_JMESPATH_QUERY = auto()
    NOT_APPLICABLE = auto()


def get_mock_recommendation_model_path(folder):
    return os.path.join(folder, MOCK_MODEL_DIR, MOCK_RECOMMENDATION_MODEL_FILENAME)


def _parse_entity(entity):
    kwargs = {}
    kwargs['recommendations'] = entity.get('recommendations', [])
    kwargs['arguments'] = entity.get('arguments', '')
    kwargs['extension'] = entity.get('extension', None)
    kwargs['user_fault_type'] = UserFaultType[entity.get('user_fault_type', 'not_applicable').upper()]
    return RecommendationData(**kwargs)


class MockRecommendationModel():
    MODEL = None
    NO_DATA = None

    @classmethod
    def load(cls, path):
        content = None
        model = {}

        with open(os.path.join(path), 'r') as test_recommendation_data_file:
            content = json.load(test_recommendation_data_file)

        for command, entity in content.items():
            model[command] = _parse_entity(entity)

        cls.MODEL = model
        cls.NO_DATA = _parse_entity({})

    @classmethod
    def create_mock_aladdin_service_http_response(cls, command):
        mock_response = requests.Response()
        mock_response.status_code = HTTPStatus.OK.value
        data = cls.get_recommendation_data(command)
        mock_response._content = bytes(json.dumps(data.recommendations), 'utf-8')  # pylint: disable=protected-access
        return mock_response

    @classmethod
    def get_recommendation_data(cls, command):
        return cls.MODEL.get(command, cls.NO_DATA)

    @classmethod
    def get_recommendations(cls, command):
        data = cls.get_recommendation_data(command)
        recommendations = [FailureRecoveryRecommendation(recommendation) for recommendation in data.recommendations]
        return recommendations

    @classmethod
    def get_test_cases(cls):
        cases = []
        model = cls.MODEL or {}
        for command, entity in model.items():
            cases.append((command, entity))
        return cases


@contextmanager
def mock_aladdin_service_call(command):
    handlers = {}
    handler = handlers.get(command, MockRecommendationModel.create_mock_aladdin_service_http_response)

    with mock.patch('requests.get', return_value=handler(command)):
        yield None
