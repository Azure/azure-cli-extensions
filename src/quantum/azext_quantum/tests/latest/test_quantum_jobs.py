# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse, live_only
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)

from .utils import TEST_WORKSPACE, TEST_RG, TEST_WORKSPACE_LOCATION, TEST_SUBS
from .utils import TEST_WORKSPACE_JOBS, TEST_RG_JOBS, TEST_WORKSPACE_LOCATION_JOBS
from ..._client_factory import _get_data_credentials
from ...operations.workspace import WorkspaceInfo
from ...operations.target import TargetInfo
from ...operations.job import _generate_submit_args, _parse_blob_url

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class QuantumJobsScenarioTest(ScenarioTest):

    def test_jobs(self):
        # set current workspace:
        self.cmd(f'az quantum workspace set -w {TEST_WORKSPACE_JOBS} -g {TEST_RG_JOBS} -l {TEST_WORKSPACE_LOCATION_JOBS}')

        # list
        targets = self.cmd('az quantum target list -o json').get_output_in_json()
        assert len(targets) > 0

    @live_only()
    def test_submit_args(self):
        ws = WorkspaceInfo(self, TEST_RG_JOBS, TEST_WORKSPACE_JOBS, TEST_WORKSPACE_LOCATION_JOBS)
        target = TargetInfo(self, 'ionq.simulator')

        token = _get_data_credentials(self.cli_ctx, TEST_SUBS).get_token().token
        assert len(token) > 0

        args = _generate_submit_args(["--foo", "--bar"], ws, target, token, project=None, job_name=None, storage=None, shots=None)
        self.assertEquals(args[0], "dotnet")
        self.assertEquals(args[1], "run")
        self.assertEquals(args[2], "--no-build")
        self.assertIn("--", args)
        self.assertIn("submit", args)
        self.assertIn(TEST_WORKSPACE_JOBS, args)
        self.assertIn(TEST_RG_JOBS, args)
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
