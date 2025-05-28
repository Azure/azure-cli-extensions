# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


class VmwareScriptScenarioTest(ScenarioTest):
    def setUp(self):
        # https://vcrpy.readthedocs.io/en/latest/configuration.html#request-matching
        self.vcr.match_on = ['scheme', 'method', 'path', 'query']  # not 'host', 'port'
        super(VmwareScriptScenarioTest, self).setUp()

    @ResourceGroupPreparer(name_prefix='cli_test_vmware_script')
    def test_vmware_script(self):
        self.kwargs.update({
            'subscription': '12341234-1234-1234-1234-123412341234',
            'privatecloud': 'cloud1',
            'scriptExecution': 'addSsoServer',
            'scriptPackage': 'Microsoft.AVS.Management@3.0.48',
            'scriptCmdlet': 'New-ExternalSsoDomain'
        })

        count = len(self.cmd('az vmware script-package list -g {rg} -c {privatecloud}').get_output_in_json())
        self.assertEqual(count, 2, 'count expected to be 2')

        rsp = self.cmd('az vmware script-package show -g {rg} -c {privatecloud} -n {scriptPackage}').get_output_in_json()
        self.assertEqual(rsp['type'], 'Microsoft.AVS/privateClouds/scriptPackages')
        self.assertEqual(rsp['name'], self.kwargs.get('scriptPackage'))

        count = len(self.cmd('az vmware script-cmdlet list -g {rg} -c {privatecloud} -p {scriptPackage}').get_output_in_json())
        self.assertEqual(count, 2, 'count expected to be 2')

        rsp = self.cmd('az vmware script-cmdlet show -g {rg} -c {privatecloud} -p {scriptPackage} -n {scriptCmdlet}').get_output_in_json()
        self.assertEqual(rsp['type'], 'Microsoft.AVS/privateClouds/scriptPackages/scriptCmdlets')
        self.assertEqual(rsp['name'], self.kwargs.get('scriptCmdlet'))

        rsp = self.cmd('az vmware script-execution create --resource-group {rg} --private-cloud {privatecloud} --name {scriptExecution} --script-cmdlet-id "/subscriptions/{subscription}/resourceGroups/group1/providers/Microsoft.AVS/privateClouds/cloud1/scriptPackages/AVS.PowerCommands@1.0.0/scriptCmdlets/New-SsoExternalIdentitySource" --timeout P0Y0M0DT0H60M60S --retention P0Y0M60DT0H60M60S --parameter name=DomainName type=Value value=placeholderDomain.local --parameter name=BaseUserDN type=Value "value=DC=placeholder, DC=placeholder" --hidden-parameter name=Password type=SecureValue secureValue=PlaceholderPassword').get_output_in_json()
        self.assertEqual(rsp['type'], 'Microsoft.AVS/privateClouds/scriptExecutions')
        self.assertEqual(rsp['name'], self.kwargs.get('scriptExecution'))

        count = len(self.cmd('az vmware script-execution list -g {rg} -c {privatecloud}').get_output_in_json())
        self.assertEqual(count, 1, 'count expected to be 1')

        self.cmd('az vmware script-execution show -g {rg} -c {privatecloud} -n {scriptExecution}').get_output_in_json()
        self.assertEqual(rsp['type'], 'Microsoft.AVS/privateClouds/scriptExecutions')
        self.assertEqual(rsp['name'], self.kwargs.get('scriptExecution'))

        rsp = self.cmd('az vmware script-execution delete -g {rg} -c {privatecloud} -n {scriptExecution} --yes').output
        self.assertEqual(len(rsp), 0)
