import os
import json
from http import HTTPStatus
from contextlib import contextmanager

import mock
import requests

from azext_ai_did_you_mean_this.failure_recovery_recommendation import FailureRecoveryRecommendation

# mock service call context attributes
MOCK_UUID = '00000000-0000-0000-0000-000000000000'
MOCK_VERSION = '2.3.1'

# mock recommendation data constants
MOCK_INPUT_DIR = 'input'
MOCK_RECOMMENDATION_MODEL_FILENAME = 'recommendations.json'


def get_mock_recommendation_model_path(folder):
    return os.path.join(folder, MOCK_INPUT_DIR, MOCK_RECOMMENDATION_MODEL_FILENAME)


class MockRecommendationModel():
    MODEL = None

    @classmethod
    def load(cls, path):
        with open(os.path.join(path), 'r') as test_recommendation_data_file:
            cls.MODEL = json.load(test_recommendation_data_file)

    @classmethod
    def create_mock_aladdin_service_http_response(cls, command):
        mock_response = requests.Response()
        mock_response.status_code = HTTPStatus.OK.value
        data = cls.MODEL.get(command, [])
        mock_response._content = bytes(json.dumps(data), 'utf-8')  # pylint: disable=protected-access
        return mock_response

    @classmethod
    def get_recommendations(cls, command):
        recommendations = cls.MODEL.get(command, [])
        recommendations = [FailureRecoveryRecommendation(recommendation) for recommendation in recommendations]
        return recommendations


@contextmanager
def mock_aladdin_service_call(command):
    handlers = {}
    handler = handlers.get(command, MockRecommendationModel.create_mock_aladdin_service_http_response)

    with mock.patch('requests.get', return_value=handler(command)):
        yield None
