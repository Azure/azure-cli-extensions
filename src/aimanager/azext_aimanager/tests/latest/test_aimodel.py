# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

from azure.cli.core.azclierror import InvalidArgumentValueError

from azext_aimanager import custom
from azext_aimanager._validators import validate_ai_model_name
from azext_aimanager.vendored_sdks.v2026_05_02_preview import models


class MockCmd:
    def get_models(self, name, **_):
        return getattr(models, name)


class TestAIModel(unittest.TestCase):

    def setUp(self):
        self.cmd = MockCmd()
        self.client = MagicMock()

    def test_show_aimodel(self):
        self.client.get.return_value = "model"

        result = custom.show_aimodel(self.cmd, self.client, "eastus2", "9806f0c862fdd920")

        self.assertEqual(result, "model")
        self.client.get.assert_called_once_with("eastus2", "9806f0c862fdd920")

    def test_list_aimodel(self):
        self.client.list.return_value = ["model"]

        result = custom.list_aimodel(self.cmd, self.client, "eastus2")

        self.assertEqual(result, ["model"])
        self.client.list.assert_called_once_with("eastus2")

    def test_calculate_aimodel_cost_sends_empty_request_body(self):
        self.client.calculate_cost.return_value = "plans"

        result = custom.calculate_aimodel_cost(
            self.cmd, self.client, "eastus2", "9806f0c862fdd920")

        self.assertEqual(result, "plans")
        self.client.calculate_cost.assert_called_once()
        location, ai_model_name, body = self.client.calculate_cost.call_args[0]
        self.assertEqual(location, "eastus2")
        self.assertEqual(ai_model_name, "9806f0c862fdd920")
        self.assertIsInstance(body, models.CalculateCostRequest)
        self.assertEqual(dict(body), {})


class TestAIModelValidators(unittest.TestCase):

    def test_valid_name(self):
        validate_ai_model_name(SimpleNamespace(ai_model_name="9806f0c862fdd920"))

    def test_missing_name_is_allowed(self):
        validate_ai_model_name(SimpleNamespace(ai_model_name=None))
        validate_ai_model_name(SimpleNamespace())

    def test_blank_name_is_rejected(self):
        with self.assertRaises(InvalidArgumentValueError):
            validate_ai_model_name(SimpleNamespace(ai_model_name="   "))


if __name__ == '__main__':
    unittest.main()
