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

    @ResourceGroupPreparer(location='westus')
    def test_create_waf_policy_kitchen_sink(self, resource_group):
        # multi-line comment below
        """
Example command sequence:
az network front-door waf-policy create --resource-group {resource_group} --name {policyName}
az network front-door waf-policy create -g {rg} -n {wafp}
az network front-door waf-policy create -g {rg} -n {wafp} [--mode {mode}]
az network front-door waf-policy create -g {rg} -n {wafp} [--mode {mode}] [--redirecturl {url}]
az network front-door waf-policy create -g {rg} -n {wafp} [--mode {mode}] [--redirecturl {url}] [--customblockresponsecode {status code}]
az network front-door waf-policy create -g {rg} -n {wafp} [--mode {mode}] [--redirecturl {url}] [--customblockresponsecode {status code}] [--customblockresponsebody {body}]
az network front-door waf-policy create -g {rg} -n {wafp} [--mode {mode}] [--redirecturl {url}] [--customblockresponsecode {status code}] [--customblockresponsebody {body}]  [--disabled]

az network front-door waf-policy update -g {rg} -n {wafp} --tags test=best
az network front-door waf-policy update -g {rg} -n {wafp} --tags test=best  [--mode {mode}]
az network front-door waf-policy update -g {rg} -n {wafp} --tags test=best  [--mode {mode}] [--redirecturl {url}]
az network front-door waf-policy update -g {rg} -n {wafp} --tags test=best  [--mode {mode}] [--redirecturl {url}] [--customblockresponsecode {status code}]
az network front-door waf-policy update -g {rg} -n {wafp} --tags test=best  [--mode {mode}] [--redirecturl {url}] [--customblockresponsecode {status code}] [--customblockresponsebody {body}]
az network front-door waf-policy update -g {rg} -n {wafp} --tags test=best  [--mode {mode}] [--redirecturl {url}] [--customblockresponsecode {status code}] [--customblockresponsebody {body}]  [--disabled]
az network front-door waf-policy show -g {rg} -n {wafp}
az network front-door waf-policy list -g {rg}
az network front-door waf-policy delete -g {rg} -n {wafp}
az network front-door waf-policy rule create -g {rg} --policy-name {wafp} -n {rule} --priority 50 --action log --rule-type ratelimitrule --ratelimitduration 60 --ratelimitthreshold 10000
az network front-door waf-policy rule create -g {rg} --policy-name {wafp} -n {rule} --priority 50 --action log --rule-type ratelimitrule --disabled --ratelimitduration 60 --ratelimitthreshold 10000
az network front-door waf-policy rule create -g {rg} --policy-name {wafp} -n {rule} --priority 50 --action log --rule-type matchrule
az network front-door waf-policy rule create -g {rg} --policy-name {wafp} -n {rule} --priority 50 --action log --rule-type matchrule --disabled
az network front-door waf-policy rule update -g {rg} --policy-name {wafp} -n {rule} [--priority 75] [--action log] [--disabled] [--ratelimitduration 60] [--ratelimitthreshold 10000]
az network front-door waf-policy rule delete -g {rg} --policy-name {wafp} -n {rule}
az network front-door waf-policy rule show -g {rg} --policy-name {wafp} -n {rule}
az network front-door waf-policy rule list -g {rg} --policy-name {wafp}
az network front-door waf-policy rule delete -g {rg} --policy-name {wafp} -n {rule2}
az network front-door waf-policy rule list -g {rg} --policy-name {wafp}
az network front-door waf-policy rule match-condition add -g {rg} --policy-name {wafp} -n {rule} --match-variable RequestHeaders.value --operator contains --values foo boo
az network front-door waf-policy rule match-condition add -g {rg} --policy-name {wafp} -n {rule} --match-variable RequestHeaders.value --operator contains --values foo boo [--negate]
az network front-door waf-policy rule match-condition add -g {rg} --policy-name {wafp} -n {rule} --match-variable RequestHeaders.value --operator contains --values foo boo [--negate] [--transforms Lowercase UrlDecode]
az network front-door waf-policy rule match-condition remove -g {rg} --policy-name {wafp} -n {rule} --index 1
az network front-door waf-policy rule match-condition list -g {rg} --policy-name {wafp} -n {rule}
az network front-door waf-policy managed-rules create -g {rg} --policy-name {wafp} --type {type} --version {version}
az network front-door waf-policy managed-rules delete -g {rg} --policy-name {wafp} --type {type}
az network front-door waf-policy managed-rules override add -g {rg} --policy-name {wafp} --type {type} --rulegroupid {rulegroupid} --ruleid {ruleid} [--action {action}] [--disabled]
az network front-door waf-policy managed-rules override remove -g {rg} --policy-name {wafp} --type {type} --rulegroupid {rulegroupid} --ruleid {ruleid}
az network front-door waf-policy managed-rules list -g {rg} --policy-name {wafp}
az network front-door waf-policy managed-rule-definition list
"""

        subscription = self.current_subscription()
        policyName = self.create_random_name(prefix='cli', length=24)
        ruleName = self.create_random_name(prefix='cli', length=24)
        frontdoorName = self.create_random_name(prefix='cli', length=24)
        cmd = 'az network front-door waf-policy create -g {resource_group} -n block-policy --mode Block'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertIn('customRules', result)
        self.assertIn('managedRules', result)
        self.assertIn('id', result)

        cmd = 'az network front-door waf-policy create -g {resource_group} -n detection-redirect-policy --mode Detection --redirecturl www.microsoft.com'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertIn('customRules', result)
        self.assertIn('managedRules', result)
        self.assertIn('id', result)

        cmd = 'az network front-door waf-policy create -g {resource_group} -n detection-cbc-policy --mode Detection --redirecturl www.microsoft.com --customblockresponsecode 512'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertIn('customRules', result)
        self.assertIn('managedRules', result)
        self.assertIn('id', result)

        cmd = 'az network front-door waf-policy create -g {resource_group} -n detection-cbb-policy --mode Detection --redirecturl www.microsoft.com --customblockresponsecode 512 --customblockresponsebody "custom block body"'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertIn('customRules', result)
        self.assertIn('managedRules', result)
        self.assertIn('id', result)

        cmd = 'az network front-door waf-policy create -g {resource_group} -n detection-disabled-policy --mode Detection --disabled'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertIn('customRules', result)
        self.assertIn('managedRules', result)
        self.assertIn('id', result)


        cmd = 'az network front-door waf-policy update -g {resource_group} -n detection-disabled-policy --mode Detection --disabled'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertIn('customRules', result)
        self.assertIn('managedRules', result)
        self.assertIn('id', result)
az network front-door waf-policy update -g {rg} -n {wafp} --tags test=best
az network front-door waf-policy update -g {rg} -n {wafp} --tags test=best  [--mode {mode}]
az network front-door waf-policy update -g {rg} -n {wafp} --tags test=best  [--mode {mode}] [--redirecturl {url}]
az network front-door waf-policy update -g {rg} -n {wafp} --tags test=best  [--mode {mode}] [--redirecturl {url}] [--customblockresponsecode {status code}]
az network front-door waf-policy update -g {rg} -n {wafp} --tags test=best  [--mode {mode}] [--redirecturl {url}] [--customblockresponsecode {status code}] [--customblockresponsebody {body}]
az network front-door waf-policy update -g {rg} -n {wafp} --tags test=best  [--mode {mode}] [--redirecturl {url}] [--customblockresponsecode {status code}] [--customblockresponsebody {body}]  [--disabled]


        cmd = 'az network front-door waf-policy create -g {resource_group} -n block-policy --mode Block'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertIn('customRules', result)
        self.assertIn('managedRules', result)
        self.assertIn('id', result)

        cmd = 'az network front-door waf-policy create -g {resource_group} -n block-policy --mode Block'.format(**locals())
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
