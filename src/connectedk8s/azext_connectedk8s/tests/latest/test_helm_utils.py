# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
import mock
import os

import azext_connectedk8s._helm_utils as helm_utils

class HelmUtilsTest(unittest.TestCase):

    def test_get_chart_path(self):

        mocked_HelmCoreUtils = mock.Mock()
        mocked_instance = mocked_HelmCoreUtils.return_value
        mocked_instance.pull_helm_chart.return_value = None

        with mock.patch('azext_connectedk8s._helm_utils.HelmCoreUtils', mocked_HelmCoreUtils):
            try:
                chart_path = helm_utils.get_chart_path("test_registry_path", None, None)
            except Exception as e:
                self.fail("No exception should be raised")

            self.assertEqual(os.path.join(os.path.join(os.path.expanduser('~'), '.azure', 'AzureArcCharts'), 'azure-arc-k8sagents'), chart_path)

    def test_get_helm_registry(self):
        