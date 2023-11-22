# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
from unittest.mock import Mock, patch

from azext_aks_preview.__init__ import register_aks_preview_resource_type
from azext_aks_preview._client_factory import CUSTOM_MGMT_AKS_PREVIEW
from azext_aks_preview.managed_cluster_decorator import (
    AKSPreviewManagedClusterModels,
)
from azext_aks_preview.custom import (
    aks_stop,
)
from azext_aks_preview.tests.latest.mocks import MockCLI, MockClient, MockCmd


class TestCustomCommand(unittest.TestCase):
    def setUp(self):
        # manually register CUSTOM_MGMT_AKS_PREVIEW
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)
        self.models = AKSPreviewManagedClusterModels(self.cmd, CUSTOM_MGMT_AKS_PREVIEW)
        self.client = MockClient()

    def test_aks_stop(self):
        # public cluster: call begin_stop without prompt
        mc_1 = self.models.ManagedCluster(location="test_location")
        self.client.get = Mock(
            return_value=mc_1
        )
        self.client.begin_stop = Mock(
            return_value=None
        )
        self.assertEqual(aks_stop(self.cmd, self.client, "rg", "name"), None)

        # private cluster: return None when prompt is False
        mc_2 = self.models.ManagedCluster(location="test_location")
        api_server_access_profile = self.models.ManagedClusterAPIServerAccessProfile()
        api_server_access_profile.enable_private_cluster = True
        mc_2.api_server_access_profile = api_server_access_profile
        self.client.get = Mock(
            return_value=mc_2
        )
        with patch(
            "azext_aks_preview.custom.prompt_y_n",
            return_value=False,
        ):
            self.assertEqual(aks_stop(self.cmd, self.client, "rg", "name"), None)

        # private cluster: call begin_stop with --yes
        mc_3 = self.models.ManagedCluster(location="test_location")
        api_server_access_profile = self.models.ManagedClusterAPIServerAccessProfile()
        api_server_access_profile.enable_private_cluster = True
        mc_3.api_server_access_profile = api_server_access_profile
        self.client.get = Mock(
            return_value=mc_3
        )
        self.client.begin_stop = Mock(
            return_value=None
        )
        self.assertEqual(aks_stop(self.cmd, self.client, "rg", "name", False, True), None)

        # private cluster: call begin_stop when prompt is True
        mc_4 = self.models.ManagedCluster(location="test_location")
        api_server_access_profile = self.models.ManagedClusterAPIServerAccessProfile()
        api_server_access_profile.enable_private_cluster = True
        mc_4.api_server_access_profile = api_server_access_profile
        self.client.get = Mock(
            return_value=mc_4
        )
        self.client.begin_stop = Mock(
            return_value=None
        )
        with patch(
            "azext_aks_preview.custom.prompt_y_n",
            return_value=True,
        ):
            self.assertEqual(aks_stop(self.cmd, self.client, "rg", "name"), None)



if __name__ == '__main__':
    unittest.main()
