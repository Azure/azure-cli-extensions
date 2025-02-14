# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from os import path
import os
from unittest import mock
from unittest.mock import MagicMock
from azure.cli.core.mock import DummyCli
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from azext_acrcssc.cssc import (create_update_continuous_patch_v1, delete_continuous_patch_v1, list_continuous_patch_v1, acr_cssc_dry_run, cancel_continuous_patch_runs, track_scan_progress)


class AcrcsscScenarioTest(ScenarioTest):
    def __init__(self, method_name, config_file=None, recording_name=None, recording_processors=None, replay_processors=None, recording_patches=None, replay_patches=None, random_config_dir=False):
        super().__init__(method_name, config_file, recording_name, recording_processors, replay_processors, recording_patches, replay_patches, random_config_dir)
        
        cmd = mock.MagicMock()
        cmd.cli_ctx = DummyCli()
        registry = MagicMock()
        registry.name = "mockregistry"
        registry.id = f"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/mockrg/providers/Microsoft.ContainerRegistry/registries/{registry.name}"
        config = MagicMock()
    
    @mock.patch("azext_acrcssc._validators.check_continuous_task_exists")
    @mock.patch("azext_acrcssc.helper._deployment.validate_template")
    @mock.patch("azext_acrcssc.helper._deployment.deploy_template")
    @mock.patch("azure.cli.core.util.get_file_json")
    @mock.patch("azext_acrcssc.helper._ociartifactoperations.create_oci_artifact_continuous_patch")
    @mock.patch("azext_acrcssc..helper._taskoperations._trigger_task_run")
    def test_create_acrcssc(self, mock_get_file_json, mock_deploy_template, mock_validate_template, mock_check_continuous_task_exists, mock_create_oci_artifact_continuous_patch):
        mock_check_continuous_task_exists.return_value = False
        #mock_get_file_json.return_value = "{\"repositories\":[{\"repository\":\"mockrepo\",\"tags\":[\"mocktag\"]}],\"tag-convention\":\"floating\",\"version\":\"v1\"}"
        
        # test regular create
        result = create_update_continuous_patch_v1(self.cmd, self.registry, self.config, "1d", False, False, True)
        
        # test with run_immediately
        result = create_update_continuous_patch_v1(self.cmd, self.registry, self.config, "1d", False, False, True)
        
        # test with dryrun
    
    # @patch("azext_acrcssc._validators.check_continuous_task_exists")
    # def test_update_acrcssc(self):
    #     #mock_check_continuous_task_exists.return_value = True
    
    # def test_dryrun_acrcssc(self):
    
    # def test_delete_acrcssc(self):
        
    # def test_show_acrcssc(self):
    
    # def test_cancel_runs_acrcssc(self):
    
    # def test_list_acrcssc(self):
