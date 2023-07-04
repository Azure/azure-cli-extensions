# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from dataclasses import dataclass
import json
from unittest.mock import patch
from tempfile import TemporaryDirectory
from typing import Any, Dict

from azext_aosm.custom import generate_design_config, build_design

mock_nsd_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mock_nsd")


class TestNSDGenerator():
    def test_generate_config(self):
        """
        Test generating a config file for a VNF.
        """
        starting_directory = os.getcwd()
        with TemporaryDirectory() as test_dir:
            os.chdir(test_dir)

            try:
                generate_design_config()
                assert os.path.exists("input.json")
            finally:
                os.chdir(starting_directory)

    @patch("azext_aosm.custom.cf_resources")
    def test_build(self, cf_resources):
        """
        Test building the NSD bicep templates.
        """
        # We don't want to get details from a real NFD (calling out to Azure) in a UT.
        # Therefore we pass in a fake client to supply the deployment parameters from
        # the "NFD".
        deploy_parameters = {
            "$schema": "https://json-schema.org/draft-07/schema#",
            "title": "DeployParametersSchema",
            "type": "object",
            "properties": {
                "location": {
                    "type": "string"
                },
                "subnetName": {
                    "type": "string"
                },
                "virtualNetworkId": {
                    "type": "string"
                },
                "sshPublicKeyAdmin": {
                    "type": "string"
                }
            }
        }

        deploy_parameters_string = json.dumps(deploy_parameters)

        @dataclass
        class NFDV:
            deploy_parameters: Dict[str, Any]

        nfdv = NFDV(deploy_parameters_string)

        class NFDVs():
            def get(self, **_):
                return nfdv

        class AOSMClient():
            def __init__(self) -> None:
                self.network_function_definition_versions = NFDVs()

        mock_client = AOSMClient()

        class FakeCmd():
            def __init__(self) -> None:
                self.cli_ctx = None

        cmd = FakeCmd()

        starting_directory = os.getcwd()
        with TemporaryDirectory() as test_dir:
            os.chdir(test_dir)

            try:
                build_design(
                    cmd,
                    client=mock_client, 
                    config_file=os.path.join(mock_nsd_folder, "input.json")
                )
                assert os.path.exists("nsd-bicep-templates")
            finally:
                os.chdir(starting_directory)
