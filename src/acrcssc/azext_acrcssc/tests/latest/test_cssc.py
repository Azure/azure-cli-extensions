# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest import mock
from unittest.mock import MagicMock
from azext_acrcssc.cssc import create_acrcssc, update_acrcssc, delete_acrcssc, show_acrcssc, cancel_runs, list_scan_status

class AcrcsscTest(unittest.TestCase):
    def __init__(self, method_name):
        super().__init__(method_name)
        self.cmd = mock.MagicMock()
        self.cmd.cli_ctx = MagicMock()
        self.registry = MagicMock()
        self.registry.name = "mockregistry"
        self.registry.id = f"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/mockrg/providers/Microsoft.ContainerRegistry/registries/{self.registry.name}"
        self.config = MagicMock()

    @mock.patch("azext_acrcssc.cssc._perform_continuous_patch_operation")
    def test_create_acrcssc(self, mock_perform_continuous_patch_operation):
        create_acrcssc(self.cmd, "mockrg", self.registry.name, "continuouspatchv1", "mockconfig", "1d", False, False)
        mock_perform_continuous_patch_operation.assert_called_once_with(self.cmd, "mockrg", self.registry.name, "mockconfig", "1d", False, False, is_create=True)

    @mock.patch("azext_acrcssc.cssc._perform_continuous_patch_operation")
    def test_update_acrcssc(self, mock_perform_continuous_patch_operation):
        update_acrcssc(self.cmd, "mockrg", self.registry.name, "continuouspatchv1", "mockconfig", "1d", False, False)
        mock_perform_continuous_patch_operation.assert_called_once_with(self.cmd, "mockrg", self.registry.name, "mockconfig", "1d", False, False, is_create=False)

    @mock.patch("azext_acrcssc.cssc.delete_continuous_patch_v1")
    @mock.patch("azext_acrcssc.cssc.cf_acr_registries")
    @mock.patch("azure.cli.core.util.user_confirmation")
    def test_delete_acrcssc(self, mock_user_confirmation, mock_cf_acr_registries, mock_delete_continuous_patch_v1):
        mock_cf_acr_registries.return_value.get.return_value = self.registry
        delete_acrcssc(self.cmd, "mockrg", self.registry.name, "continuouspatchv1", True)
        mock_delete_continuous_patch_v1.assert_called_once_with(self.cmd, self.registry, yes=True)

    @mock.patch("azext_acrcssc.cssc.list_continuous_patch_v1")
    @mock.patch("azext_acrcssc.cssc.cf_acr_registries")
    def test_show_acrcssc(self, mock_cf_acr_registries, mock_list_continuous_patch_v1):
        mock_cf_acr_registries.return_value.get.return_value = self.registry
        show_acrcssc(self.cmd, "mockrg", self.registry.name, "continuouspatchv1")
        mock_list_continuous_patch_v1.assert_called_once_with(self.cmd, self.registry)

    @mock.patch("azext_acrcssc.cssc.cancel_continuous_patch_runs")
    def test_cancel_runs(self, mock_cancel_continuous_patch_runs):
        cancel_runs(self.cmd, "mockrg", self.registry.name, "continuouspatchv1")
        mock_cancel_continuous_patch_runs.assert_called_once_with(self.cmd, "mockrg", self.registry.name)

    @mock.patch("azext_acrcssc.cssc.track_scan_progress")
    @mock.patch("azext_acrcssc.cssc.cf_acr_registries")
    def test_list_scan_status(self, mock_cf_acr_registries, mock_track_scan_progress):
        mock_cf_acr_registries.return_value.get.return_value = self.registry
        list_scan_status(self.cmd, self.registry.name, "mockrg", workflow_type="continuouspatchv1", status="mockstatus")
        mock_track_scan_progress.assert_called_once_with(self.cmd, "mockrg", self.registry, "mockstatus")
