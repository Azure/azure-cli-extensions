# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from azure.cli.core.azclierror import ClientRequestError
from azure.core import MatchConditions
from azure.core.exceptions import ResourceNotFoundError

from azext_aimanager import custom
from azext_aimanager.vendored_sdks.v2026_05_02_preview import models


class MockCmd:
    def get_models(self, name, **_):
        return getattr(models, name)


class TestModelSource(unittest.TestCase):

    def setUp(self):
        self.cmd = MockCmd()

    def test_construct_wraps_inline_credential(self):
        source = custom._construct_modelsource(
            self.cmd, "HuggingFace", description="team catalog", credential="hf_secret")

        self.assertEqual(source.properties.source_type, "HuggingFace")
        self.assertEqual(source.properties.description, "team catalog")
        self.assertEqual(source.properties.credential.inline.value, "hf_secret")

    def test_construct_omits_credential_when_absent(self):
        source = custom._construct_modelsource(self.cmd, "HuggingFace")

        self.assertIsNone(source.properties.credential)

    def test_add_raises_when_source_exists(self):
        client = MagicMock()
        client.get.return_value = SimpleNamespace()
        with self.assertRaises(ClientRequestError):
            custom.add_modelsource(
                self.cmd, client, "rg", "manager", "source", "HuggingFace")
        client.begin_create_or_update.assert_not_called()

    @patch.object(custom, "sdk_no_wait")
    @patch.object(custom, "_construct_modelsource")
    def test_add_creates_when_absent(self, construct_modelsource, sdk_no_wait):
        client = MagicMock()
        client.get.side_effect = ResourceNotFoundError()
        source = object()
        construct_modelsource.return_value = source
        sdk_no_wait.return_value = "result"

        result = custom.add_modelsource(
            self.cmd, client, "rg", "manager", "source", "HuggingFace",
            description="team catalog", credential="hf_secret")

        self.assertEqual(result, "result")
        construct_modelsource.assert_called_once_with(
            self.cmd, "HuggingFace", "team catalog", "hf_secret")
        sdk_no_wait.assert_called_once_with(
            False,
            client.begin_create_or_update,
            "rg",
            "manager",
            "source",
            source,
            headers={},
        )

    def test_update_raises_when_source_missing(self):
        client = MagicMock()
        client.get.side_effect = ResourceNotFoundError()
        with self.assertRaises(ClientRequestError):
            custom.update_modelsource(self.cmd, client, "rg", "manager", "source")
        client.begin_create_or_update.assert_not_called()

    def test_delete_raises_when_source_missing(self):
        client = MagicMock()
        client.get.side_effect = ResourceNotFoundError()
        with self.assertRaises(ClientRequestError):
            custom.delete_modelsource(self.cmd, client, "rg", "manager", "source")
        client.begin_delete.assert_not_called()

    @patch.object(custom, "sdk_no_wait")
    def test_delete_calls_begin_delete(self, sdk_no_wait):
        client = MagicMock()
        client.get.return_value = SimpleNamespace()
        sdk_no_wait.return_value = "result"

        result = custom.delete_modelsource(self.cmd, client, "rg", "manager", "source")

        self.assertEqual(result, "result")
        sdk_no_wait.assert_called_once_with(
            False, client.begin_delete, "rg", "manager", "source")

    def test_list_calls_sdk_list(self):
        client = MagicMock()
        client.list.return_value = ["source"]

        result = custom.list_modelsource(self.cmd, client, "rg", "manager")

        self.assertEqual(result, ["source"])
        client.list.assert_called_once_with("rg", "manager")

    @patch.object(custom, "sdk_no_wait")
    @patch.object(custom, "_construct_modelsource")
    def test_update_modelsource_preserves_omitted_properties_and_uses_etag(
            self, construct_modelsource, sdk_no_wait):
        existing = SimpleNamespace(
            e_tag='"etag-value"',
            properties=SimpleNamespace(
                source_type="HuggingFace",
                description="existing description",
                credential=None,
            ),
        )
        client = MagicMock()
        client.get.return_value = existing
        source = object()
        construct_modelsource.return_value = source
        sdk_no_wait.return_value = "result"

        result = custom.update_modelsource(
            self.cmd, client, "rg", "manager", "source")

        self.assertEqual(result, "result")
        construct_modelsource.assert_called_once_with(
            self.cmd,
            "HuggingFace",
            "existing description",
            None,
        )
        sdk_no_wait.assert_called_once_with(
            False,
            client.begin_create_or_update,
            "rg",
            "manager",
            "source",
            source,
            headers={},
            etag='"etag-value"',
            match_condition=MatchConditions.IfNotModified,
        )

    @patch.object(custom, "sdk_no_wait")
    @patch.object(custom, "_construct_modelsource")
    def test_update_passes_supplied_credential_and_description(
            self, construct_modelsource, sdk_no_wait):
        existing = SimpleNamespace(
            e_tag=None,
            properties=SimpleNamespace(
                source_type="HuggingFace",
                description="old description",
                credential=None,
            ),
        )
        client = MagicMock()
        client.get.return_value = existing
        construct_modelsource.return_value = object()
        sdk_no_wait.return_value = "result"

        custom.update_modelsource(
            self.cmd, client, "rg", "manager", "source",
            description="new description", credential="hf_rotated")

        # Supplied values must be forwarded verbatim, not replaced by the existing ones.
        construct_modelsource.assert_called_once_with(
            self.cmd, "HuggingFace", "new description", "hf_rotated")


if __name__ == '__main__':
    unittest.main()
