# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from azure.cli.core.azclierror import ClientRequestError, InvalidArgumentValueError
from azure.core.exceptions import ResourceNotFoundError

from azext_aimanager import custom
from azext_aimanager._validators import validate_model_source_name
from azext_aimanager.vendored_sdks.v2026_05_02_preview import models


class MockCmd:
    def get_models(self, name, **_):
        return getattr(models, name)


class TestModelSource(unittest.TestCase):

    def setUp(self):
        self.cmd = MockCmd()
        self.client = MagicMock()

    def test_construct_without_token_omits_credential(self):
        source = custom._construct_modelsource(self.cmd, "HuggingFace", "desc")

        self.assertEqual(source.properties.source_type, "HuggingFace")
        self.assertEqual(source.properties.description, "desc")
        self.assertIsNone(source.properties.credential)

    def test_construct_with_token_sets_inline_credential(self):
        source = custom._construct_modelsource(self.cmd, "HuggingFace", None, "hf_token")

        self.assertEqual(source.properties.credential.inline.value, "hf_token")

    def test_add_rejects_existing_source(self):
        self.client.get.return_value = object()

        with self.assertRaises(ClientRequestError):
            custom.add_modelsource(
                self.cmd, self.client, "rg", "manager", "source", "HuggingFace")

    def test_update_rejects_missing_source(self):
        self.client.get.side_effect = ResourceNotFoundError()

        with self.assertRaises(ClientRequestError):
            custom.update_modelsource(self.cmd, self.client, "rg", "manager", "source")

    @patch.object(custom, "sdk_no_wait")
    @patch.object(custom, "_construct_modelsource")
    def test_update_preserves_source_type_and_description(
            self, construct_modelsource, sdk_no_wait):
        self.client.get.return_value = SimpleNamespace(
            properties=SimpleNamespace(
                source_type="HuggingFace",
                description="existing description",
            ))
        construct_modelsource.return_value = "model-source"
        sdk_no_wait.return_value = "result"

        result = custom.update_modelsource(
            self.cmd, self.client, "rg", "manager", "source", token="hf_new")

        self.assertEqual(result, "result")
        construct_modelsource.assert_called_once_with(
            self.cmd, "HuggingFace", "existing description", "hf_new")
        sdk_no_wait.assert_called_once_with(
            False,
            self.client.begin_create_or_update,
            "rg",
            "manager",
            "source",
            "model-source",
            headers={},
        )

    def test_delete_rejects_missing_source(self):
        self.client.get.side_effect = ResourceNotFoundError()

        with self.assertRaises(ClientRequestError):
            custom.delete_modelsource(self.cmd, self.client, "rg", "manager", "source")

    def test_list_uses_ai_manager_scope(self):
        self.client.list.return_value = ["source"]

        result = custom.list_modelsource(self.cmd, self.client, "rg", "manager")

        self.assertEqual(result, ["source"])
        self.client.list.assert_called_once_with("rg", "manager")


class TestModelSourceValidators(unittest.TestCase):

    def test_valid_name(self):
        validate_model_source_name(SimpleNamespace(model_source_name="hf"))

    def test_missing_name_is_allowed(self):
        validate_model_source_name(SimpleNamespace(model_source_name=None))
        validate_model_source_name(SimpleNamespace())

    def test_blank_name_is_rejected(self):
        with self.assertRaises(InvalidArgumentValueError):
            validate_model_source_name(SimpleNamespace(model_source_name="  "))


if __name__ == '__main__':
    unittest.main()
