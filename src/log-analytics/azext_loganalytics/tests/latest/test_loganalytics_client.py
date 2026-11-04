# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from types import SimpleNamespace
from unittest import mock, TestCase

from azure.cli.core.cloud import CloudEndpoints, CloudNameEnum

from azext_loganalytics.aaz.latest._clients import (
    AAZMicrosoftOperationalinsightsDataPlaneClient as Client,
)


class LogAnalyticsClientConfigurationTests(TestCase):

    def test_cloud_host_template_fallbacks(self):
        cloud_cases = (
            (CloudNameEnum.AzureCloud, "https://api.loganalytics.io"),
            (CloudNameEnum.AzureChinaCloud, "https://api.loganalytics.azure.cn"),
            (CloudNameEnum.AzureUSGovernment, "https://api.loganalytics.us"),
        )

        for cloud_name, expected_endpoint in cloud_cases:
            with self.subTest(cloud_name=cloud_name):
                ctx = SimpleNamespace(
                    cli_ctx=SimpleNamespace(
                        cloud=SimpleNamespace(
                            name=cloud_name,
                            endpoints=CloudEndpoints(log_analytics_resource_id=None),
                        )
                    )
                )

                with mock.patch.object(
                        Client, "_retrieve_value_in_arm_cloud_metadata", return_value=None):
                    endpoint = Client._build_base_url(ctx)

                self.assertEqual(endpoint, expected_endpoint)

    def test_cloud_specific_credential_scopes(self):
        credential = mock.Mock()
        cloud_cases = (
            (CloudNameEnum.AzureCloud, "https://api.loganalytics.io/.default"),
            (CloudNameEnum.AzureChinaCloud, "https://api.loganalytics.azure.cn/.default"),
            (CloudNameEnum.AzureUSGovernment, "https://api.loganalytics.us/.default"),
        )

        for cloud_name, expected_scope in cloud_cases:
            with self.subTest(cloud_name=cloud_name):
                ctx = SimpleNamespace(
                    cli_ctx=SimpleNamespace(
                        cloud=SimpleNamespace(name=cloud_name)
                    )
                )

                with mock.patch(
                        "azext_loganalytics.aaz.latest._clients.AAZClientConfiguration") as configuration:
                    Client._build_configuration(ctx, credential)

                configuration.assert_called_once_with(
                    credential=credential,
                    credential_scopes=[expected_scope],
                )
