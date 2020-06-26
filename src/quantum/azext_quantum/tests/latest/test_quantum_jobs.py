# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)

from .utils import is_private_preview_subscription, TEST_WORKSPACE, TEST_RG, TEST_SUBS
from ..._client_factory import _get_data_credentials
from ...operations.workspace import WorkspaceInfo
from ...operations.target import TargetInfo
from ...operations.job import _generate_submit_args, _parse_blob_url

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class QuantumScenarioTest(ScenarioTest):

    def test_targets(self):
        # Since azure quantum is still in private preview, we require
        # these tests to run in a specific subscription (AzureQuantum-test)
        # if running somewhere else, just skip
        if not is_private_preview_subscription(self):
            self.skipTest(f"Need to run azure quantum tests in subscription {TEST_SUBS}")

        # set current workspace:
        self.cmd(f'az quantum workspace set -g {TEST_RG} -w {TEST_WORKSPACE}')

        # list
        targets = self.cmd('az quantum target list -o json').get_output_in_json()
        assert len(targets) > 0

    def test_submit_args(self):
        # Since azure quantum is still in private preview, we require
        # these tests to run in a specific subscription (AzureQuantum-test)
        # if running somewhere else, just skip
        if not is_private_preview_subscription(self):
            self.skipTest(f"Need to run azure quantum tests in subscription {TEST_SUBS}")

        ws = WorkspaceInfo(self, TEST_RG, TEST_WORKSPACE)
        target = TargetInfo(self, 'ionq.simulator')

        token = _get_data_credentials(self.cli_ctx, TEST_SUBS).get_token().token
        assert len(token) > 0

        args = _generate_submit_args(["--foo", "--bar"], ws, target, token, project=None, job_name=None, storage=None, shots=None)
        self.assertEquals(args[0], "dotnet")
        self.assertEquals(args[1], "run")
        self.assertEquals(args[2], "--no-build")
        self.assertIn("--", args)
        self.assertIn("submit", args)
        self.assertIn(TEST_SUBS, args)
        self.assertIn(TEST_WORKSPACE, args)
        self.assertIn(TEST_RG, args)
        self.assertIn("ionq.simulator", args)
        self.assertIn("--aad-token", args)
        self.assertIn(token, args)
        self.assertIn("--foo", args)
        self.assertIn("--bar", args)
        self.assertNotIn("--project", args)
        self.assertNotIn("--job-name", args)
        self.assertNotIn("--storage", args)
        self.assertNotIn("--shots", args)

        args = _generate_submit_args(["--foo", "--bar"], ws, target, token, "../other/path", "job-name", 1234, "az-stor")
        self.assertEquals(args[0], "dotnet")
        self.assertEquals(args[1], "run")
        self.assertEquals(args[2], "--no-build")
        self.assertIn("../other/path", args)
        self.assertIn("job-name", args)
        self.assertIn("az-stor", args)
        self.assertIn(1234, args)
        self.assertIn("--project", args)
        self.assertIn("--job-name", args)
        self.assertIn("--storage", args)
        self.assertIn("--shots", args)

    def test_parse_blob_url(self):
        sas = "sv=2018-03-28&sr=c&sig=some-sig&sp=racwl"
        url = f"https://getest2.blob.core.windows.net/qio/rawOutputData?{sas}"
        args = _parse_blob_url(url)

        self.assertEquals(args['account_name'], "getest2")
        self.assertEquals(args['container'], "qio")
        self.assertEquals(args['blob'], "rawOutputData")
        self.assertEquals(args['sas_token'], sas)
