# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest.mock import Mock, patch

from azext_aks_preview._helpers import (
    _fuzzy_match,
    check_is_private_link_cluster,
    get_cluster_snapshot,
    get_cluster_snapshot_by_snapshot_id,
    get_nodepool_snapshot,
    get_nodepool_snapshot_by_snapshot_id,
)
from azext_aks_preview.__init__ import register_aks_preview_resource_type
from azext_aks_preview._client_factory import CUSTOM_MGMT_AKS_PREVIEW
from azext_aks_preview.managed_cluster_decorator import (
    AKSPreviewManagedClusterModels,
)
from azure.cli.core.azclierror import (
    BadRequestError,
    InvalidArgumentValueError,
    ResourceNotFoundError,
)
from azure.core.exceptions import AzureError, HttpResponseError
from azext_aks_preview.tests.latest.mocks import MockCLI, MockCmd


class TestFuzzyMatch(unittest.TestCase):
    def setUp(self):
        self.expected = ['bord', 'birdy', 'fbird', 'bir', 'ird', 'birdwaj']

    def test_fuzzy_match(self):
        result = _fuzzy_match(
            "bird", ["plane", "bord", "birdy", "fbird", "bir", "ird", "birdwaj", "bored", "biron", "bead"])

        self.assertCountEqual(result, self.expected)
        self.assertListEqual(result, self.expected)


class GetNodepoolSnapShotTestCase(unittest.TestCase):
    def test_get_nodepool_snapshot_by_snapshot_id(self):
        with self.assertRaises(InvalidArgumentValueError):
            get_nodepool_snapshot_by_snapshot_id("mock_cli_ctx", "")

        mock_snapshot = Mock()
        with patch(
            "azext_aks_preview._helpers.get_nodepool_snapshot", return_value=mock_snapshot
        ) as mock_get_snapshot:
            snapshot = get_nodepool_snapshot_by_snapshot_id(
                "mock_cli_ctx",
                "/subscriptions/test_sub/resourcegroups/test_rg/providers/microsoft.containerservice/snapshots/test_np_snapshot",
            )
            self.assertEqual(snapshot, mock_snapshot)
            mock_get_snapshot.assert_called_once_with("mock_cli_ctx", "test_sub", "test_rg", "test_np_snapshot")

    def test_get_nodepool_snapshot(self):
        mock_snapshot = Mock()
        mock_snapshot_operations = Mock(get=Mock(return_value=mock_snapshot))
        with patch("azext_aks_preview._helpers.get_nodepool_snapshots_client", return_value=mock_snapshot_operations):
            snapshot = get_nodepool_snapshot("mock_cli_ctx", "test_sub", "mock_rg", "mock_snapshot_name")
            self.assertEqual(snapshot, mock_snapshot)

        mock_snapshot_operations_2 = Mock(get=Mock(side_effect=AzureError("mock snapshot was not found")))
        with patch(
            "azext_aks_preview._helpers.get_nodepool_snapshots_client", return_value=mock_snapshot_operations_2
        ), self.assertRaises(ResourceNotFoundError):
            get_nodepool_snapshot("mock_cli_ctx", "test_sub", "mock_rg", "mock_snapshot_name")

        http_response_error = HttpResponseError()
        http_response_error.status_code = 400
        http_response_error.message = "test_error_msg"
        mock_snapshot_operations_3 = Mock(get=Mock(side_effect=http_response_error))
        with patch(
            "azext_aks_preview._helpers.get_nodepool_snapshots_client", return_value=mock_snapshot_operations_3
        ), self.assertRaises(BadRequestError):
            get_nodepool_snapshot("mock_cli_ctx", "test_sub", "mock_rg", "mock_snapshot_name")


class GetManagedClusterSnapShotTestCase(unittest.TestCase):
    def test_get_cluster_snapshot_by_snapshot_id(self):
        with self.assertRaises(InvalidArgumentValueError):
            get_cluster_snapshot_by_snapshot_id("mock_cli_ctx", "")

        mock_snapshot = Mock()
        with patch(
            "azext_aks_preview._helpers.get_cluster_snapshot", return_value=mock_snapshot
        ) as mock_get_snapshot:
            snapshot = get_cluster_snapshot_by_snapshot_id(
                "mock_cli_ctx",
                "/subscriptions/test_sub/resourcegroups/test_rg/providers/microsoft.containerservice/managedclustersnapshots/test_mc_snapshot",
            )
            self.assertEqual(snapshot, mock_snapshot)
            mock_get_snapshot.assert_called_once_with("mock_cli_ctx", "test_sub", "test_rg", "test_mc_snapshot")

    def test_get_cluster_snapshot(self):
        mock_snapshot = Mock()
        mock_snapshot_operations = Mock(get=Mock(return_value=mock_snapshot))
        with patch("azext_aks_preview._helpers.get_mc_snapshots_client", return_value=mock_snapshot_operations):
            snapshot = get_cluster_snapshot("mock_cli_ctx", "test_sub", "mock_rg", "mock_snapshot_name")
            self.assertEqual(snapshot, mock_snapshot)

        mock_snapshot_operations_2 = Mock(get=Mock(side_effect=AzureError("mock snapshot was not found")))
        with patch(
            "azext_aks_preview._helpers.get_mc_snapshots_client", return_value=mock_snapshot_operations_2
        ), self.assertRaises(ResourceNotFoundError):
            get_cluster_snapshot("mock_cli_ctx", "test_sub", "mock_rg", "mock_snapshot_name")

        http_response_error = HttpResponseError()
        http_response_error.status_code = 400
        http_response_error.message = "test_error_msg"
        mock_snapshot_operations_3 = Mock(get=Mock(side_effect=http_response_error))
        with patch(
            "azext_aks_preview._helpers.get_mc_snapshots_client", return_value=mock_snapshot_operations_3
        ), self.assertRaises(BadRequestError):
            get_cluster_snapshot("mock_cli_ctx", "test_sub", "mock_rg", "mock_snapshot_name")


class CheckManagedClusterTestCase(unittest.TestCase):
    def setUp(self):
        # manually register CUSTOM_MGMT_AKS_PREVIEW
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)
        # store all the models used by nat gateway
        self.models = AKSPreviewManagedClusterModels(self.cmd, CUSTOM_MGMT_AKS_PREVIEW)

    def test_check_is_private_link_cluster(self):
        mc_1 = self.models.ManagedCluster(location="test_location")
        self.assertEqual(check_is_private_link_cluster(mc_1), False)

        mc_2 = self.models.ManagedCluster(location="test_location")
        api_server_access_profile = self.models.ManagedClusterAPIServerAccessProfile()
        api_server_access_profile.enable_private_cluster = True
        api_server_access_profile.enable_vnet_integration = True
        self.assertEqual(check_is_private_link_cluster(mc_2), False)

        mc_3 = self.models.ManagedCluster(location="test_location")
        api_server_access_profile = self.models.ManagedClusterAPIServerAccessProfile()
        api_server_access_profile.enable_private_cluster = True
        mc_3.api_server_access_profile = api_server_access_profile
        self.assertEqual(check_is_private_link_cluster(mc_3), True)


if __name__ == "__main__":
    unittest.main()
