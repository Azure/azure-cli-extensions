# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from typing import no_type_check
import unittest
from unittest.mock import Mock, patch

from azure.core.exceptions import HttpResponseError

from azext_k8s_extension import custom
from .MockClasses import MockCLIContext, MockCommand
from azext_k8s_extension.custom import is_dogfood_cluster


class TestIsDogfoodCluster(unittest.TestCase):
    def test_dogfood_cluster(self):
        cmd = MockCommand()
        cmd.cli_ctx.cloud.endpoints.resource_manager = (
            "https://api-dogfood.resources.windows-int.net"
        )
        assert is_dogfood_cluster(cmd)

    def test_dogfood_cluster_with_slash(self):
        cmd = MockCommand()
        cmd.cli_ctx.cloud.endpoints.resource_manager = (
            "https://api-dogfood.resources.windows-int.net/"
        )
        assert is_dogfood_cluster(cmd)

    def test_longer_hostname(self):
        cmd = MockCommand()
        cmd.cli_ctx.cloud.endpoints.resource_manager = (
            "https://api-dogfood.resources.windows-int.otherwebsite.net/"
        )
        assert not is_dogfood_cluster(cmd)

    def malformed_url(self):
        cmd = MockCommand()
        cmd.cli_ctx.cloud.endpoints.resource_manager = "htmalformed~2987493"
        assert not is_dogfood_cluster(cmd)

    def test_prod_cluster(self):
        cmd = MockCommand()
        cmd.cli_ctx.cloud.endpoints.resource_manager = "https://management.azure.com"
        assert not is_dogfood_cluster(cmd)


class TestDeleteK8sExtension(unittest.TestCase):
    def test_not_found_is_already_deleted(self):
        client = Mock()
        client.get.side_effect = HttpResponseError(
            message="Extension not found",
            response=Mock(status_code=404, reason="Not Found", headers={}),
        )

        with patch.object(custom, "ExtensionFactory") as factory:
            with self.assertLogs(custom.logger, level="WARNING") as logs:
                result = custom.delete_k8s_extension(
                    MockCommand(), client, "rg", "cluster", "extension", "managedClusters"
                )

        self.assertIsNone(result)
        self.assertIn("nothing to delete", logs.output[0])
        factory.assert_not_called()
        client.begin_delete.assert_not_called()

    def test_non_404_lookup_errors_propagate(self):
        for status_code in (401, 403, 429, 500, 503, None):
            with self.subTest(status_code=status_code):
                client = Mock()
                error = HttpResponseError(
                    message="Extension lookup failed",
                    response=Mock(status_code=status_code, reason="Lookup failed", headers={}),
                )
                client.get.side_effect = error

                with patch.object(custom, "ExtensionFactory") as factory:
                    with self.assertRaises(HttpResponseError) as raised:
                        custom.delete_k8s_extension(
                            MockCommand(), client, "rg", "cluster", "extension", "managedClusters"
                        )

                self.assertIs(raised.exception, error)
                factory.assert_not_called()
                client.begin_delete.assert_not_called()

    @patch.object(custom, "sdk_no_wait")
    @patch.object(custom, "ExtensionFactory")
    def test_existing_extension_is_deleted(self, factory, sdk_no_wait):
        cmd = MockCommand()
        client = Mock()
        client.get.return_value.extension_type = "Microsoft.PodSnapshot"

        result = custom.delete_k8s_extension(
            cmd, client, "rg", "cluster", "extension", "managedClusters",
            no_wait=True, yes=True, force=True,
        )

        client.get.assert_called_once_with(
            "rg", "Microsoft.ContainerService", "managedClusters", "cluster", "extension"
        )
        factory.assert_called_once_with("microsoft.podsnapshot")
        factory.return_value.Delete.assert_called_once_with(
            cmd, client, "rg", "cluster", "extension", "managedClusters",
            "Microsoft.ContainerService", True,
        )
        sdk_no_wait.assert_called_once_with(
            True, client.begin_delete, "rg", "Microsoft.ContainerService",
            "managedClusters", "cluster", "extension", force_delete=True,
        )
        self.assertIs(result, sdk_no_wait.return_value)
