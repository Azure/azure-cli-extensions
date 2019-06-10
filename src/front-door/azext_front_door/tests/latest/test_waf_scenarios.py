# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.testsdk import (ScenarioTest, JMESPathCheck, ResourceGroupPreparer,
                               api_version_constraint)
from .frontdoor_test_util import WafScenarioMixin


class WafTests(WafScenarioMixin, ScenarioTest):
    @ResourceGroupPreparer(location='westus')
    def test_create_waf_policy_with_custom_rule(self, resource_group):
        # multi-line comment below
        """
Example command sequence:
az network front-door waf-policy create --resource-group {resource_group} --name {policyName}
az network front-door waf-policy rule create  -g {resource_group} --policy-name {policyName} -n {ruleName} --priority 6 --rule-type MatchRule --action Block --match-condition RequestBody RegEx "something"
az network front-door create  --resource-group {resource_group} --backend-address www.example.com --name {frontdoorName}
# wait two minutes
az network front-door update --name {frontdoorName}--resource-group {resource_group} --set "FrontendEndpoints[0].WebApplicationFirewallPolicyLink.id=/subscriptions/{subscriptionId}/resourcegroups/{resource_group}/providers/Microsoft.Network/frontdoorwebapplicationfirewallpolicies/{policyName}"
"""

        subscription = self.current_subscription()
        policyName = self.create_random_name(prefix='cli', length=24)
        ruleName = self.create_random_name(prefix='cli', length=24)
        frontdoorName = self.create_random_name(prefix='cli', length=24)
        cmd = 'az network front-door waf-policy create --resource-group {resource_group} --name {policyName}'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()


        self.assertIn('customRules', result)
        self.assertIn('managedRules', result)
        self.assertIn('id', result)

        cmd = 'az network front-door waf-policy rule create  -g {resource_group} --policy-name {policyName} -n {ruleName} --priority 6 --rule-type MatchRule --action Block --match-condition RequestBody RegEx "something"'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()

        self.assertIn('customRules', result)
        self.assertEqual(result['customRules']['rules'][0]['matchConditions'][0]['matchValue'][0], "something")

        cmd = 'az network front-door create  --resource-group {resource_group} --backend-address www.example.com --name {frontdoorName}'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()

        self.assertIn('frontendEndpoints', result)
        hostName = result['frontendEndpoints'][0]['hostName']
        self.assertTrue(hostName != None)

        wafId = '/subscriptions/{subscription}/resourcegroups/{resource_group}/providers/Microsoft.Network/frontdoorwebapplicationfirewallpolicies/{policyName}'.format(**locals())
        cmd = 'az network front-door update --name {frontdoorName} --resource-group {resource_group} --set "FrontendEndpoints[0].WebApplicationFirewallPolicyLink.id={wafId}"'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertIn('frontendEndpoints', result)
        self.assertEqual(result ['frontendEndpoints'][0]['hostName'], hostName)
        self.assertEqual(result ['frontendEndpoints'][0]['webApplicationFirewallPolicyLink']['id'], wafId)

        if( self.is_live ):
            import requests

            import time
            time.sleep(480)
            r = requests.post('http://{hostName}/'.format(**locals()), data = "'key':'value'")
            self.assertEqual(r.status_code, 200)

            r = requests.post('http://{hostName}/'.format(**locals()), data = "'key':'something'")
            self.assertEqual(r.status_code, 403)
