# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck, record_only)


class FrontDoorBYOCScenarioTests(ScenarioTest):

    # @record_only()  # This test requires resources in the specific subscription
    def test_frontend_endpoint_byoc_latest_version(self):
        resource_group = "CliDevReservedGroup"
        front_door = "frontdoorclitest"
        frontend_endpoint_name = "afdbyoc-latest-localdev-cdn-azure-cn"
        # Use the latest version of the secret
        byoc_checks = [JMESPathCheck('customHttpsConfiguration.secretVersion', None),
                       JMESPathCheck('customHttpsProvisioningState', "Enabling"),
                       JMESPathCheck('customHttpsProvisioningSubstate', "ImportingUserProvidedCertificate")]
        self.cmd(f'network front-door frontend-endpoint enable-https -f {front_door} -g {resource_group} -n {frontend_endpoint_name} '
                 '--certificate-source AzureKeyVault '
                 f'--vault-id /subscriptions/{self.get_subscription_id()}/resourceGroups/CliDevReservedGroup/providers/Microsoft.KeyVault/vaults/clibyoc-int '
                 '--secret-name localdev-multi', checks=byoc_checks)

        self.cmd(f'network front-door frontend-endpoint wait -f {front_door} -g {resource_group} -n {frontend_endpoint_name} '
                 "--custom \"customHttpsProvisioningState=='Enabled'\"")

        self.cmd(f'network front-door frontend-endpoint disable-https -f {front_door} -g {resource_group} -n {frontend_endpoint_name}')

        self.cmd(f'network front-door frontend-endpoint wait -f {front_door} -g {resource_group} -n {frontend_endpoint_name} '
                 "--custom \"customHttpsProvisioningState=='Disabled'\"")

    # @record_only()  # This test requires resources in the specific subscription
    def test_frontend_endpoint_byoc_specific_version(self):
        resource_group = "CliDevReservedGroup"
        front_door = "frontdoorclitest"
        frontend_endpoint_name = "afdbyoc-specific-localdev-cdn-azure-cn"

        # Use the specific version of the secret
        byoc_checks = [JMESPathCheck('customHttpsConfiguration.secretVersion', "6244bbfa61c241d78403a6e394cc2d30"),
                       JMESPathCheck('customHttpsProvisioningState', "Enabling"),
                       JMESPathCheck('customHttpsProvisioningSubstate', "ImportingUserProvidedCertificate")]
        self.cmd(f'network front-door frontend-endpoint enable-https -f {front_door} -g {resource_group} -n {frontend_endpoint_name} '
                 '--certificate-source AzureKeyVault '
                 f'--vault-id /subscriptions/{self.get_subscription_id()}/resourceGroups/CliDevReservedGroup/providers/Microsoft.KeyVault/vaults/clibyoc-int '
                 '--secret-name localdev-multi '
                 '--secret-version 6244bbfa61c241d78403a6e394cc2d30', checks=byoc_checks)

        self.cmd(f'network front-door frontend-endpoint wait -f {front_door} -g {resource_group} -n {frontend_endpoint_name} '
                 "--custom \"customHttpsProvisioningState=='Enabled'\"")

        self.cmd(f'network front-door frontend-endpoint disable-https -f {front_door} -g {resource_group} -n {frontend_endpoint_name}')

        self.cmd(f'network front-door frontend-endpoint wait -f {front_door} -g {resource_group} -n {frontend_endpoint_name} '
                 "--custom \"customHttpsProvisioningState=='Disabled'\"")
