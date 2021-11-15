# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest

from unittest.mock import patch
from unittest.mock import MagicMock

from azure.cli.core.azclierror import  ArgumentUsageError

import azext_connectedk8s._helm_core_utils as hc_utils

class HelmCoreUtilsTest(unittest.TestCase):

    def test_pull_helm_chart(self):
        helm_utils = hc_utils.HelmCoreUtils()
        helm_utils.set_kube_configuration("test_kube_config", "test_kube_context")
        helm_utils._HelmCoreUtils__execute_helm_command = MagicMock(return_value="test_url")
        try:
            helm_utils.pull_helm_chart("registry_path_url")
        except Exception as e:
            self.fail("No exception should be raised")

    def test_export_helm_chart(self):
        helm_utils = hc_utils.HelmCoreUtils()
        helm_utils._HelmCoreUtils__execute_helm_command = MagicMock(return_value="test_url")
        try:
            helm_utils.export_helm_chart("registry_path_url", "export_path")
        except Exception as e:
            self.fail("No exception should be raised")

    def test_add_helm_repo(self):
        helm_utils = hc_utils.HelmCoreUtils()
        helm_utils._HelmCoreUtils__execute_helm_command = MagicMock(return_value="test_url")
        try:
            helm_utils.add_helm_repo("repo_name", "repo_url")
        except Exception as e:
            self.fail("No exception should be raised")

    def test_check_helm_version(self):
        helm_utils = hc_utils.HelmCoreUtils()
        helm_utils._HelmCoreUtils__execute_helm_command = MagicMock(return_value=2.3)
        try:
            self.assertEqual(2.3, helm_utils.check_helm_version())
        except Exception as e:
            self.fail("No exception should be raised")

    def test_get_release_namespace(self):
        helm_utils = hc_utils.HelmCoreUtils()
        helm_utils._HelmCoreUtils__execute_helm_command = MagicMock(return_value="[{\"name\":\"azure-arc\",\"namespace\":\"default\",\"revision\":\"2\",\"updated\":\"2021-11-08 10:33:54.8752323 +0000 UTC\",\"status\":\"deployed\",\"chart\":\"azure-arc-k8sagents-1.5.3\",\"app_version\":\"1.0\"}]")
        self.assertEqual("default", helm_utils.get_release_namespace())

        helm_utils._HelmCoreUtils__execute_helm_command = MagicMock(return_value="invalidJSON")
        self.assertEqual(None, helm_utils.get_release_namespace())

        helm_utils._HelmCoreUtils__execute_helm_command = MagicMock(return_value="[{\"name\":\"azure\",\"namespace\":\"default\",\"revision\":\"2\",\"updated\":\"2021-11-08 10:33:54.8752323 +0000 UTC\",\"status\":\"deployed\",\"chart\":\"azure-arc-k8sagents-1.5.3\",\"app_version\":\"1.0\"}]")
        self.assertEqual(None, helm_utils.get_release_namespace())

    def test_get_all_helm_values(self):
        helm_utils = hc_utils.HelmCoreUtils()
        helm_utils._HelmCoreUtils__execute_helm_command = MagicMock(return_value="[{\"name\":\"azure-arc\",\"namespace\":\"default\",\"revision\":\"2\",\"updated\":\"2021-11-08 10:33:54.8752323 +0000 UTC\",\"status\":\"deployed\",\"chart\":\"azure-arc-k8sagents-1.5.3\",\"app_version\":\"1.0\"}]")
        values = helm_utils.get_all_helm_values("test_release")
        for value in values:
            self.assertEqual(value['name'], 'azure-arc')

        try:
            helm_utils._HelmCoreUtils__execute_helm_command = MagicMock(return_value=AssertionError("test Exception"))
            helm_utils.get_all_helm_values("test_release")
            self.fail("Exception should be raised")
        except Exception as e:
            pass
