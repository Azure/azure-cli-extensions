# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-few-public-methods

from azure.cli.testsdk import ScenarioTest


class AzureSubscriptionScenarioTest(ScenarioTest):
    def test_create_subscription(self):
        enrollment_accounts = self.cmd('billing enrollment-account list').get_output_in_json()
        result = self.cmd('account create --enrollment-account-name {} --offer-type MS-AZR-0148P'.format(enrollment_accounts[0].name)).get_output_in_json()
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.subscription_link)
