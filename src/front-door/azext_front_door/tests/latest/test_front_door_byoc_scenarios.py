# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck)


class FrontDoorBYOCScenarioTests(ScenarioTest):

    @unittest.skip("The test is not working as existing enable-https's implemention has ignored the LROPoller which will cause failures in test TearDown")
    def test_frontend_endpoint_byoc_latest_version(self):
        resource_group = "bzhanafdtest"
        front_door = "frontdoorpstest2"
        frontend_endpoint_name = "afd-byoc-latest-localdev-cdn-azure-cn"
        # Use the latest version of the secret
        byoc_checks = [JMESPathCheck('customHttpsConfiguration.secretVersion', None),
                       JMESPathCheck('customHttpsProvisioningState', "Enabling"),
                       JMESPathCheck('customHttpsProvisioningSubstate', "ImportingUserProvidedCertificate")]
        self.cmd(f'network front-door frontend-endpoint enable-https -f {front_door} -g {resource_group} -n {frontend_endpoint_name} '
                 '--certificate-source AzureKeyVault '
                 f'--vault-id /subscriptions/{self.get_subscription_id()}/resourceGroups/bzhanafdtest/providers/Microsoft.KeyVault/vaults/bzhanbyostest '
                 '--secret-name frontdoorpstest2', checks=byoc_checks)

    @unittest.skip("The test is not working as existing enable-https's implemention has ignored the LROPoller which will cause failures in test TearDown")
    def test_frontend_endpoint_byoc_specific_version(self):
        resource_group = "bzhanafdtest"
        front_door = "frontdoorpstest2"
        frontend_endpoint_name = "afd-byoc-specific-localdev-cdn-azure-cn"

        # Use the specific version of the secret
        byoc_checks = [JMESPathCheck('customHttpsConfiguration.secretVersion', "d6b1f0ffd2a142efb2a8a89289802c77"),
                       JMESPathCheck('customHttpsProvisioningState', "Enabling"),
                       JMESPathCheck('customHttpsProvisioningSubstate', "ImportingUserProvidedCertificate")]
        self.cmd(f'network front-door frontend-endpoint enable-https -f {front_door} -g {resource_group} -n {frontend_endpoint_name} '
                 '--certificate-source AzureKeyVault '
                 f'--vault-id /subscriptions/{self.get_subscription_id()}/resourceGroups/bzhanafdtest/providers/Microsoft.KeyVault/vaults/bzhanbyostest '
                 '--secret-name frontdoorpstest2 '
                 '--secret-version d6b1f0ffd2a142efb2a8a89289802c77', checks=byoc_checks)
