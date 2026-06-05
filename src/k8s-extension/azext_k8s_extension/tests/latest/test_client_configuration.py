# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest

from azure.core.credentials import AccessToken

from azext_k8s_extension.vendored_sdks import SourceControlConfigurationClient
from azext_k8s_extension.vendored_sdks._configuration import (
    SourceControlConfigurationClientConfiguration as SyncConfiguration,
)
from azext_k8s_extension.vendored_sdks.aio import (
    SourceControlConfigurationClient as AsyncSourceControlConfigurationClient,
)
from azext_k8s_extension.vendored_sdks.aio._configuration import (
    SourceControlConfigurationClientConfiguration as AsyncConfiguration,
)


class DummyCredential:
    def get_token(self, *scopes, **kwargs):
        return AccessToken("test-token", 253402300799)


class DummyAsyncCredential:
    async def get_token(self, *scopes, **kwargs):
        return AccessToken("test-token", 253402300799)


class TestSourceControlConfigurationCompatibility(unittest.TestCase):
    def test_sync_configuration_exposes_base_url(self):
        config = SyncConfiguration(
            credential=DummyCredential(),
            subscription_id="00000000-0000-0000-0000-000000000000",
            base_url="https://management.azure.com",
        )

        self.assertTrue(hasattr(config, "base_url"))
        self.assertEqual(config.base_url, "https://management.azure.com")
        self.assertTrue(hasattr(config, "api_version"))
        self.assertTrue(hasattr(config, "polling_interval"))

    def test_sync_client_passes_base_url_to_configuration(self):
        client = SourceControlConfigurationClient(
            credential=DummyCredential(),
            subscription_id="00000000-0000-0000-0000-000000000000",
            base_url="https://management.azure.com",
        )

        self.assertEqual(client._config.base_url, "https://management.azure.com")

    def test_async_configuration_exposes_base_url(self):
        config = AsyncConfiguration(
            credential=DummyAsyncCredential(),
            subscription_id="00000000-0000-0000-0000-000000000000",
            base_url="https://management.azure.com",
        )

        self.assertTrue(hasattr(config, "base_url"))
        self.assertEqual(config.base_url, "https://management.azure.com")
        self.assertTrue(hasattr(config, "api_version"))
        self.assertTrue(hasattr(config, "polling_interval"))

    def test_async_client_passes_base_url_to_configuration(self):
        client = AsyncSourceControlConfigurationClient(
            credential=DummyAsyncCredential(),
            subscription_id="00000000-0000-0000-0000-000000000000",
            base_url="https://management.azure.com",
        )

        self.assertEqual(client._config.base_url, "https://management.azure.com")
