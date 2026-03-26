# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.testsdk import (ScenarioTest, JMESPathCheck, ResourceGroupPreparer,
                               api_version_constraint, live_only)

from .frontdoor_test_util import WafScenarioMixin
from knack.cli import CLIError
from azure.core.exceptions import (HttpResponseError)


class WafTests(WafScenarioMixin, ScenarioTest):
    @ResourceGroupPreparer(location='westus', additional_tags={'owner': 'jingnanxu'})
    def test_waf_captcha(self, resource_group):
        blockpolicy = self.create_random_name(prefix='cli', length=24)
        cmd = 'az network front-door waf-policy create -g {resource_group} -n {blockpolicy} --captcha-expiration-in-minutes 5 --mode prevention --sku Premium_AzureFrontDoor'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(result['name'], blockpolicy)
        self.assertEqual(result['policySettings']['captchaExpirationInMinutes'], 5)
        cmd = 'az network front-door waf-policy update -g {resource_group} -n {blockpolicy} --captcha-expiration-in-minutes 12'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(result['policySettings']['captchaExpirationInMinutes'], 12)

    @ResourceGroupPreparer(location='westus', additional_tags={'owner': 'jingnanxu'})
    def test_waf_log_scrubbing(self, resource_group):
        blockpolicy = self.create_random_name(prefix='cli', length=24)
        cmd = 'az network front-door waf-policy create -g {resource_group} -n {blockpolicy} --mode prevention --sku Premium_AzureFrontDoor'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(result['name'], blockpolicy)
        self.assertEqual(result['policySettings']['mode'], "Prevention")
        self.assertEqual(result['policySettings']['requestBodyCheck'], "Enabled")
        self.assertIn('customRules', result)
        self.assertIn('managedRules', result)
        self.assertIn('id', result)
        options = '--log-scrubbing \"{{scrubbing-rules:[{{match-variable:QueryStringArgNames,selector-match-operator:EqualsAny}}],state:Enabled}}\"'
        cmd = 'az network front-door waf-policy update -g {resource_group} -n {blockpolicy}'.format(**locals())
        result = self.cmd(cmd + ' ' + options).get_output_in_json()
        self.assertEqual(result['policySettings']['scrubbingRules'][0]['state'], "Enabled")

    @ResourceGroupPreparer(location='westus', additional_tags={'owner': 'jingnanxu'})
    def test_waf_policy_basic(self, resource_group):
        # multi-line comment below
        """
    az network front-door waf-policy create --resource-group {resource_group} --name {policyName}
az network front-door waf-policy create -g {resource_group} -n {policyName}
az network front-door waf-policy create -g {resource_group} -n {policyName} [--mode {mode}]
az network front-door waf-policy create -g {resource_group} -n {policyName} [--mode {mode}] [--redirect-url {url}]
az network front-door waf-policy create -g {resource_group} -n {policyName} [--mode {mode}] [--redirect-url {url}] [--custom-block-response-status-code {status code}]
az network front-door waf-policy create -g {resource_group} -n {policyName} [--mode {mode}] [--redirect-url {url}] [--custom-block-response-status-code {status code}] [--custom-block-response-body {body}]
az network front-door waf-policy create -g {resource_group} -n {policyName} [--mode {mode}] [--redirect-url {url}] [--custom-block-response-status-code {status code}] [--custom-block-response-body {body}]  [--disabled]

az network front-door waf-policy update -g {resource_group} -n {policyName} --tags test=best
az network front-door waf-policy update -g {resource_group} -n {policyName} --tags test=best  [--mode {mode}]
az network front-door waf-policy update -g {resource_group} -n {policyName} --tags test=best  [--mode {mode}] [--redirect-url {url}]
az network front-door waf-policy update -g {resource_group} -n {policyName} --tags test=best  [--mode {mode}] [--redirect-url {url}] [--custom-block-response-status-code {status code}]
az network front-door waf-policy update -g {resource_group} -n {policyName} --tags test=best  [--mode {mode}] [--redirect-url {url}] [--custom-block-response-status-code {status code}] [--custom-block-response-body {body}]
az network front-door waf-policy update -g {resource_group} -n {policyName} --tags test=best  [--mode {mode}] [--redirect-url {url}] [--custom-block-response-status-code {status code}] [--custom-block-response-body {body}]  [--disabled]
az network front-door waf-policy show -g {resource_group} -n {policyName}
az network front-door waf-policy list -g {resource_group}
az network front-door waf-policy delete -g {resource_group} -n {policyName}
"""
        subscription = self.current_subscription()
        blockpolicy = self.create_random_name(prefix='cli', length=24)
        ruleName = self.create_random_name(prefix='cli', length=24)
        cmd = 'az network front-door waf-policy create -g {resource_group} -n {blockpolicy} --mode prevention'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(result['name'], blockpolicy)
        self.assertEqual(result['policySettings']['mode'], "Prevention")
        self.assertEqual(result['policySettings']['requestBodyCheck'], "Enabled")
        self.assertIn('customRules', result)
        self.assertIn('managedRules', result)
        self.assertIn('id', result)
        self.assertEqual(result['sku']['name'], "Premium_AzureFrontDoor")

        standardskupolicy = self.create_random_name(prefix='cli', length=24)
        cmd = 'az network front-door waf-policy create -g {resource_group} -n {standardskupolicy} --mode prevention --sku Premium_AzureFrontDoor'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(result['name'], standardskupolicy)
        self.assertEqual(result['policySettings']['mode'], "Prevention")
        self.assertEqual(result['policySettings']['requestBodyCheck'], "Enabled")
        self.assertIn('customRules', result)
        self.assertIn('managedRules', result)
        self.assertIn('id', result)
        self.assertEqual(result['sku']['name'], "Premium_AzureFrontDoor")

        detectionredirectpolicy = self.create_random_name(prefix='cli', length=24)
        cmd = 'az network front-door waf-policy create -g {resource_group} -n {detectionredirectpolicy} --mode Detection --redirect-url http://www.microsoft.com --sku Premium_AzureFrontDoor'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(result['name'], detectionredirectpolicy)
        self.assertEqual(result['policySettings']['mode'], "Detection")
        self.assertEqual(result['policySettings']['redirectUrl'], "http://www.microsoft.com")
        self.assertEqual(result['policySettings']['requestBodyCheck'], "Enabled")
        self.assertIn('customRules', result)
        self.assertIn('managedRules', result)
        self.assertIn('id', result)
        self.assertEqual(result['sku']['name'], "Premium_AzureFrontDoor")

        detectioncbcpolicy = self.create_random_name(prefix='cli', length=24)
        cmd = 'az network front-door waf-policy create -g {resource_group} -n {detectioncbcpolicy} --mode Detection --redirect-url http://www.microsoft.com --custom-block-response-status-code 406 --sku Premium_AzureFrontDoor'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(result['name'], detectioncbcpolicy)
        self.assertEqual(result['policySettings']['mode'], "Detection")
        self.assertEqual(result['policySettings']['redirectUrl'], "http://www.microsoft.com")
        self.assertEqual(result['policySettings']['customBlockResponseStatusCode'], 406)
        self.assertEqual(result['policySettings']['requestBodyCheck'], "Enabled")
        self.assertIn('customRules', result)
        self.assertIn('managedRules', result)
        self.assertIn('id', result)
        self.assertEqual(result['sku']['name'], "Premium_AzureFrontDoor")

        detectioncbbpolicy = self.create_random_name(prefix='cli', length=24)
        cmd = 'az network front-door waf-policy create -g {resource_group} -n {detectioncbbpolicy} --mode Detection --redirect-url http://www.microsoft.com --custom-block-response-status-code 406 --custom-block-response-body YiBvZHk='.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(result['name'], detectioncbbpolicy)
        self.assertEqual(result['policySettings']['mode'], "Detection")
        self.assertEqual(result['policySettings']['enabledState'], "Enabled")
        self.assertEqual(result['policySettings']['redirectUrl'], "http://www.microsoft.com")
        self.assertEqual(result['policySettings']['customBlockResponseStatusCode'], 406)
        self.assertEqual(result['policySettings']['customBlockResponseBody'], "YiBvZHk=")
        self.assertEqual(result['policySettings']['requestBodyCheck'], "Enabled")
        self.assertIn('customRules', result)
        self.assertIn('managedRules', result)
        self.assertIn('id', result)
        self.assertEqual(result['sku']['name'], "Premium_AzureFrontDoor")

        detectiondisabledpolicy = self.create_random_name(prefix='cli', length=24)
        cmd = 'az network front-door waf-policy create -g {resource_group} -n {detectiondisabledpolicy} --mode Detection --disabled'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(result['name'], detectiondisabledpolicy)
        self.assertEqual(result['policySettings']['mode'], "Detection")
        self.assertEqual(result['policySettings']['enabledState'], "Disabled")
        self.assertEqual(result['policySettings']['requestBodyCheck'], "Enabled")
        self.assertIn('customRules', result)
        self.assertIn('managedRules', result)
        self.assertIn('id', result)
        self.assertEqual(result['sku']['name'], "Premium_AzureFrontDoor")

        cmd = 'az network front-door waf-policy update -g {resource_group} -n {detectiondisabledpolicy} --mode Detection'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertIn('customRules', result)
        self.assertIn('managedRules', result)
        self.assertIn('id', result)
        self.assertEqual(result['policySettings']['enabledState'], "Enabled")
        self.assertEqual(result['policySettings']['requestBodyCheck'], "Enabled")
        self.assertEqual(result['sku']['name'], "Premium_AzureFrontDoor")

        cmd = 'az network front-door waf-policy update -g {resource_group} -n {blockpolicy} --tags test=best'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(result['name'], blockpolicy)
        self.assertEqual(result['policySettings']['mode'], "Prevention")
        # TODO uncomment once API support for updating tags is fixed :-O
        # self.assertEqual(result['tags'], { 'test': 'best' })
        self.assertIn('customRules', result)
        self.assertIn('managedRules', result)
        self.assertIn('id', result)
        self.assertEqual(result['sku']['name'], "Premium_AzureFrontDoor")

        cmd = 'az network front-door waf-policy update -g {resource_group} -n {blockpolicy} --mode detection --sku Premium_AzureFrontDoor'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(result['name'], blockpolicy)
        self.assertEqual(result['policySettings']['mode'], "Detection")
        self.assertEqual(result['policySettings']['requestBodyCheck'], "Enabled")
        self.assertEqual(result['sku']['name'], "Premium_AzureFrontDoor")

        cmd = 'az network front-door waf-policy update -g {resource_group} -n {blockpolicy} --mode prevention --redirect-url http://www.microsoft.com'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(result['name'], blockpolicy)
        self.assertEqual(result['policySettings']['mode'], "Prevention")
        self.assertEqual(result['policySettings']['redirectUrl'], 'http://www.microsoft.com')
        self.assertEqual(result['sku']['name'], "Premium_AzureFrontDoor")

        cmd = 'az network front-door waf-policy update -g {resource_group} -n {blockpolicy} --custom-block-response-status-code 406'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(result['name'], blockpolicy)
        self.assertEqual(result['policySettings']['mode'], "Prevention")
        self.assertEqual(result['policySettings']['customBlockResponseStatusCode'], 406)
        self.assertEqual(result['policySettings']['requestBodyCheck'], "Enabled")
        self.assertEqual(result['sku']['name'], "Premium_AzureFrontDoor")

        cmd = 'az network front-door waf-policy update -g {resource_group} -n {blockpolicy} --custom-block-response-status-code 405 --custom-block-response-body YiBvZHk='.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(result['name'], blockpolicy)
        self.assertEqual(result['policySettings']['mode'], "Prevention")
        self.assertEqual(result['policySettings']['customBlockResponseStatusCode'], 405)
        self.assertEqual(result['policySettings']['customBlockResponseBody'], "YiBvZHk=")
        self.assertEqual(result['policySettings']['requestBodyCheck'], "Enabled")
        self.assertEqual(result['sku']['name'], "Premium_AzureFrontDoor")

        cmd = 'az network front-door waf-policy update -g {resource_group} -n {blockpolicy} --disabled'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(result['name'], blockpolicy)
        self.assertEqual(result['policySettings']['enabledState'], "Disabled")
        self.assertEqual(result['policySettings']['requestBodyCheck'], "Enabled")
        self.assertEqual(result['sku']['name'], "Premium_AzureFrontDoor")

        cmd = 'az network front-door waf-policy show -g {resource_group} -n {blockpolicy}'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(result['name'], blockpolicy)
        # spot check
        self.assertEqual(result['policySettings']['enabledState'], "Disabled")
        self.assertEqual(result['policySettings']['customBlockResponseStatusCode'], 405)
        self.assertEqual(result['policySettings']['requestBodyCheck'], "Enabled")
        self.assertEqual(result['sku']['name'], "Premium_AzureFrontDoor")

        cmd = 'az network front-door waf-policy list -g {resource_group}'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(len(result), 6)
        blockPolicyObject = [policy for policy in result if policy['name'] == blockpolicy][0]
        self.assertEqual(blockPolicyObject['name'], blockpolicy)

        cmd = 'az network front-door waf-policy delete -g {resource_group} -n {blockpolicy}'.format(**locals())
        result = self.cmd(cmd)

        cmd = 'az network front-door waf-policy list -g {resource_group}'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(len(result), 5)
        self.assertEqual(len([policy for policy in result if policy['name'] == blockpolicy]), 0)

    @ResourceGroupPreparer(location='westus', additional_tags={'owner': 'jingnanxu'})
    def test_waf_policy_managed_rules(self, resource_group):
        # multi-line comment below
        """
Example command sequence:
az network front-door waf-policy managed-rules add -g {resource_group} --policy-name {policyName} --type {type} --version {version}
az network front-door waf-policy managed-rules override add -g {resource_group} --policy-name {policyName} --type {type} --rule-group-id {rulegroupid} --rule-id {ruleid} [--action {action}] [--disabled]
az network front-door waf-policy managed-rules override remove -g {resource_group} --policy-name {policyName} --type {type} --rule-group-id {rulegroupid} --rule-id {ruleid}
az network front-door waf-policy managed-rules list -g {resource_group} --policy-name {policyName}
az network front-door waf-policy managed-rules remove -g {resource_group} --policy-name {policyName} --type {type}
az network front-door waf-policy managed-rule-definition list
"""
        subscription = self.current_subscription()
        policyName = self.create_random_name(prefix='cli', length=24)
        ruleName = self.create_random_name(prefix='cli', length=24)
        frontdoorName = self.create_random_name(prefix='cli', length=24)

        cmd = 'az network front-door waf-policy create --resource-group {resource_group} --name {policyName} --sku Premium_AzureFrontDoor'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()

        self.assertEqual(result['sku']['name'], "Premium_AzureFrontDoor")

        type = "DefaultRuleSet"
        version = "1.0"
        cmd = 'az network front-door waf-policy managed-rules add -g {resource_group} --policy-name {policyName} --type {type} --version {version}'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()

        self.assertIn('managedRules', result)
        self.assertEqual(result['managedRules']['managedRuleSets'][0]['ruleSetType'], type)

        rulegroupid = "SQLI"
        ruleid = "942100"
        action = "Block"
        cmd = 'az network front-door waf-policy managed-rules override add -g {resource_group} --policy-name {policyName} --type {type} --rule-group-id {rulegroupid} --rule-id {ruleid} --action {action} --disabled'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(result['managedRules']['managedRuleSets'][0]['ruleGroupOverrides'][0]["ruleGroupName"], rulegroupid)
        self.assertEqual(result['managedRules']['managedRuleSets'][0]['ruleGroupOverrides'][0]["rules"][0]["ruleId"], ruleid)
        self.assertEqual(result['managedRules']['managedRuleSets'][0]['ruleGroupOverrides'][0]["rules"][0]["action"], action)
        self.assertEqual(result['managedRules']['managedRuleSets'][0]['ruleGroupOverrides'][0]["rules"][0]["enabledState"], "Disabled")

        cmd = 'az network front-door waf-policy managed-rules override remove -g {resource_group} --policy-name {policyName} --type {type} --rule-group-id {rulegroupid} --rule-id {ruleid}'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(len(result['managedRules']['managedRuleSets'][0]['ruleGroupOverrides']), 0)

        cmd = 'az network front-door waf-policy managed-rules list -g {resource_group} --policy-name {policyName}'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['ruleSetType'], type)

        cmd = 'az network front-door waf-policy managed-rules remove -g {resource_group} --policy-name {policyName} --type {type}'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertIn('managedRules', result)
        self.assertEqual(len(result['managedRules']['managedRuleSets']), 0)

        type = "Microsoft_DefaultRuleSet"
        version = "2.0"
        action = "Block"
        cmd = 'az network front-door waf-policy managed-rules add -g {resource_group} --policy-name {policyName} --type {type} --version {version} --action {action}'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()

        self.assertIn('managedRules', result)
        self.assertEqual(result['managedRules']['managedRuleSets'][0]['ruleSetType'], type)
        self.assertEqual(result['managedRules']['managedRuleSets'][0]['ruleSetVersion'], version)
        self.assertEqual(result['managedRules']['managedRuleSets'][0]['ruleSetAction'], action)

    @ResourceGroupPreparer(location='westus', additional_tags={'owner': 'jingnanxu'})
    def test_waf_policy_managed_rules_sensitivity(self, resource_group):
        """Test adding a managed rule override with --sensitivity for DDoS rule sets."""
        policyName = self.create_random_name(prefix='cli', length=24)

        # Create a WAF policy with Premium SKU
        cmd = 'az network front-door waf-policy create -g {resource_group} -n {policyName} --sku Premium_AzureFrontDoor'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(result['sku']['name'], "Premium_AzureFrontDoor")

        # Add DDoS managed rule set
        type = "Microsoft_HTTPDDoSRuleSet"
        version = "1.0"
        cmd = 'az network front-door waf-policy managed-rules add -g {resource_group} --policy-name {policyName} --type {type} --version {version}'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertIn('managedRules', result)
        self.assertEqual(result['managedRules']['managedRuleSets'][0]['ruleSetType'], type)

        # Add override with sensitivity
        rulegroupid = "ExcessiveRequests"
        ruleid = "500100"
        action = "Log"
        sensitivity = "Low"
        cmd = 'az network front-door waf-policy managed-rules override add -g {resource_group} --policy-name {policyName} --type {type} --rule-group-id {rulegroupid} --rule-id {ruleid} --action {action} --sensitivity {sensitivity}'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        ruleGroupOverride = result['managedRules']['managedRuleSets'][0]['ruleGroupOverrides'][0]
        self.assertEqual(ruleGroupOverride['ruleGroupName'], rulegroupid)
        self.assertEqual(ruleGroupOverride['rules'][0]['ruleId'], ruleid)
        self.assertEqual(ruleGroupOverride['rules'][0]['action'], action)
        self.assertEqual(ruleGroupOverride['rules'][0]['sensitivity'], sensitivity)
        self.assertEqual(ruleGroupOverride['rules'][0]['enabledState'], 'Enabled')

        # Update override with different sensitivity
        sensitivity = "High"
        cmd = 'az network front-door waf-policy managed-rules override add -g {resource_group} --policy-name {policyName} --type {type} --rule-group-id {rulegroupid} --rule-id {ruleid} --action {action} --sensitivity {sensitivity}'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        ruleGroupOverride = result['managedRules']['managedRuleSets'][0]['ruleGroupOverrides'][0]
        self.assertEqual(ruleGroupOverride['rules'][0]['sensitivity'], sensitivity)

        # List overrides
        cmd = 'az network front-door waf-policy managed-rules override list -g {resource_group} --policy-name {policyName} --type {type}'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['rules'][0]['sensitivity'], sensitivity)

        # Remove override
        cmd = 'az network front-door waf-policy managed-rules override remove -g {resource_group} --policy-name {policyName} --type {type} --rule-group-id {rulegroupid} --rule-id {ruleid}'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(len(result['managedRules']['managedRuleSets'][0]['ruleGroupOverrides']), 0)

    @ResourceGroupPreparer(location='westus', additional_tags={'owner': 'jingnanxu'})
    def test_waf_policy_custom_rules(self, resource_group):
        # multi-line comment below
        """
Example command sequence:
az network front-door waf-policy rule create -g {resource_group} --policy-name {policyName} -n {rateLimit} --priority 10 --action log --rule-type ratelimitrule --rate-limit-duration 5 --rate-limit-threshold 10000
az network front-door waf-policy rule create -g {resource_group} --policy-name {policyName} -n {badRateLimit} --priority 20 --action log --rule-type ratelimitrule --rate-limit-threshold 10000 --defer <-- should error
az network front-door waf-policy rule create -g {resource_group} --policy-name {policyName} -n {disabledRateLimit} --priority 30 --action log --rule-type ratelimitrule --disabled --rate-limit-duration 1 --rate-limit-threshold 10000 --defer
az network front-door waf-policy rule create -g {resource_group} --policy-name {policyName} -n {match} --priority 40 --action log --rule-type matchrule --defer
az network front-door waf-policy rule update -g {resource_group} --policy-name {policyName} -n {rateLimit} [--priority 45] [--action log] [--rate-limit-duration 5] [--rate-limit-threshold 10000]
az network front-door waf-policy rule update -g {resource_group} --policy-name {policyName} -n {disabledRateLimit} [--priority 75] [--disabled] [--rate-limit-duration 5]
az network front-door waf-policy rule delete -g {resource_group} --policy-name {policyName} -n {disabledRateLimit}
az network front-door waf-policy rule show -g {resource_group} --policy-name {policyName} -n {rateLimit}
az network front-door waf-policy rule list -g {resource_group} --policy-name {policyName}
az network front-door waf-policy rule match-condition add -g {resource_group} --policy-name {policyName} -n {rateLimit} --match-variable RequestHeaders.value --operator Contains --values foo boo
az network front-door waf-policy rule match-condition add -g {resource_group} --policy-name {policyName} -n {rateLimit} --match-variable RequestHeaders --operator Contains --values foo boo <-- expect error, no selector
az network front-door waf-policy rule match-condition add -g {resource_group} --policy-name {policyName} -n {match} --match-variable RequestUri --operator Contains --values foo boo [--negate]
az network front-door waf-policy rule match-condition add -g {resource_group} --policy-name {policyName} -n {match} --match-variable RequestHeaders.value --operator Contains --values foo boo [--negate] [--transforms Lowercase UrlDecode]
az network front-door waf-policy rule match-condition remove -g {resource_group} --policy-name {policyName} -n {match} --index 1
az network front-door waf-policy rule match-condition list -g {resource_group} --policy-name {policyName} -n {match}
"""

        subscription = self.current_subscription()
        policyName = self.create_random_name(prefix='cli', length=24)
        cmd = 'az network front-door waf-policy create -g {resource_group} -n {policyName} --mode prevention'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()

        self.assertEqual(result['sku']['name'], "Premium_AzureFrontDoor")

        rateLimit = self.create_random_name(prefix='cli', length=24)
        cmd = 'az network front-door waf-policy rule create -g {resource_group} --policy-name {policyName} -n {rateLimit} --priority 10 --action log --rule-type ratelimitrule --rate-limit-duration 5 --rate-limit-threshold 10000 --match-variable RemoteAddr --operator IPMatch --values 192.168.1.0/24'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(result['customRules']['rules'][0]['rateLimitDurationInMinutes'], 5)
        self.assertEqual(result['customRules']['rules'][0]['rateLimitThreshold'], 10000)

        badRateLimit = self.create_random_name(prefix='cli', length=24)
        cmd = 'az network front-door waf-policy rule create -g {resource_group} --policy-name {policyName} -n {badRateLimit} --priority 20 --action log --rule-type ratelimitrule --rate-limit-threshold 10000 --match-variable RemoteAddr --operator IPMatch --values 192.168.1.0/24'.format(**locals())
        try:
            result = self.cmd(cmd)
            self.fail("should throw exception")
        except CLIError as e:
            self.assertEqual(str(e), "--rate-limit-duration and --rate-limit-threshold are required for a RateLimitRule")

        disabledRateLimit = self.create_random_name(prefix='cli', length=24)
        cmd = 'az network front-door waf-policy rule create -g {resource_group} --policy-name {policyName} -n {disabledRateLimit} --priority 30 --action log --rule-type ratelimitrule --disabled --rate-limit-duration 1 --rate-limit-threshold 10000 --match-variable RequestUri --operator Contains --values foo'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(result['customRules']['rules'][1]['enabledState'], "Disabled")

        match = self.create_random_name(prefix='cli', length=24)
        cmd = 'az network front-door waf-policy rule create -g {resource_group} --policy-name {policyName} -n {match} --priority 40 --action log --rule-type matchrule --match-variable RequestUri --operator Contains --values test'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(result['customRules']['rules'][2]['ruleType'], "MatchRule")

        cmd = 'az network front-door waf-policy rule update -g {resource_group} --policy-name {policyName} -n {rateLimit} --priority 45 --action block --rate-limit-duration 5 --rate-limit-threshold 10000'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(result['customRules']['rules'][0]['priority'], 45)
        self.assertEqual(result['customRules']['rules'][0]['action'], "Block")

        cmd = 'az network front-door waf-policy rule update -g {resource_group} --policy-name {policyName} -n {disabledRateLimit} --priority 75 --disabled --rate-limit-duration 1'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(result['customRules']['rules'][1]['priority'], 75)
        self.assertEqual(result['customRules']['rules'][1]['rateLimitDurationInMinutes'], 1)
        self.assertEqual(result['customRules']['rules'][1]['enabledState'], 'Disabled')

        cmd = 'az network front-door waf-policy rule match-condition add -g {resource_group} --policy-name {policyName} -n {rateLimit} --match-variable RequestHeader.value --operator Contains --values foo boo'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        # Index 1 because index 0 is the RemoteAddr condition from rule creation
        self.assertEqual(result['customRules']['rules'][0]['matchConditions'][1]['matchVariable'], 'RequestHeader')
        self.assertEqual(result['customRules']['rules'][0]['matchConditions'][1]['selector'], 'value')
        self.assertEqual(result['customRules']['rules'][0]['matchConditions'][1]['matchValue'][0], 'foo')
        self.assertEqual(result['customRules']['rules'][0]['matchConditions'][1]['matchValue'][1], 'boo')

        # This should fail because RequestHeader requires a selector
        cmd = 'az network front-door waf-policy rule match-condition add -g {resource_group} --policy-name {policyName} -n {rateLimit} --match-variable RequestHeader --operator Contains --values foo boo'.format(**locals())
        try:
            result = self.cmd(cmd)
            self.fail("should throw exception - RequestHeader requires a selector")
        except HttpResponseError as e:
            self.assertIn("Selector must be set when using RequestHeader match variable", str(e))

        cmd = 'az network front-door waf-policy rule match-condition add -g {resource_group} --policy-name {policyName} -n {disabledRateLimit} --match-variable RequestUri --operator Contains --values foo boo --negate'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        # Index 1 because index 0 is the RequestUri condition from rule creation
        self.assertEqual(result['customRules']['rules'][1]['matchConditions'][1]['matchVariable'], 'RequestUri')
        self.assertIsNone(result['customRules']['rules'][1]['matchConditions'][1].get('selector'))
        self.assertEqual(result['customRules']['rules'][1]['matchConditions'][1]['negateCondition'], True)
        self.assertEqual(result['customRules']['rules'][1]['matchConditions'][1]['matchValue'][0], 'foo')
        self.assertEqual(result['customRules']['rules'][1]['matchConditions'][1]['matchValue'][1], 'boo')

        cmd = 'az network front-door waf-policy rule match-condition add -g {resource_group} --policy-name {policyName} -n {match} --match-variable RequestUri --operator Contains --values foo boo'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        # Index 1 because index 0 is the RequestUri condition from rule creation
        self.assertEqual(result['customRules']['rules'][2]['matchConditions'][1]['matchVariable'], 'RequestUri')
        self.assertIsNone(result['customRules']['rules'][2]['matchConditions'][1].get('selector'))
        self.assertEqual(result['customRules']['rules'][2]['matchConditions'][1].get('negateCondition'), False)
        self.assertEqual(result['customRules']['rules'][2]['matchConditions'][1]['matchValue'][0], 'foo')
        self.assertEqual(result['customRules']['rules'][2]['matchConditions'][1]['matchValue'][1], 'boo')

        cmd = 'az network front-door waf-policy rule match-condition add -g {resource_group} --policy-name {policyName} -n {match} --match-variable RequestHeader.value --operator Contains --values foo boo --transforms Lowercase UrlDecode'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(result['customRules']['rules'][2]['matchConditions'][2]['matchVariable'], 'RequestHeader')
        self.assertEqual(result['customRules']['rules'][2]['matchConditions'][2]['selector'], 'value')
        self.assertEqual(result['customRules']['rules'][2]['matchConditions'][2]['matchValue'][0], 'foo')
        self.assertEqual(result['customRules']['rules'][2]['matchConditions'][2]['matchValue'][1], 'boo')
        self.assertEqual(result['customRules']['rules'][2]['matchConditions'][2]['transforms'][0], 'Lowercase')
        self.assertEqual(result['customRules']['rules'][2]['matchConditions'][2]['transforms'][1], 'UrlDecode')

        cmd = 'az network front-door waf-policy rule match-condition remove -g {resource_group} --policy-name {policyName} -n {match} --index 1'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(len(result['customRules']['rules'][2]['matchConditions']), 2)

        cmd = 'az network front-door waf-policy rule match-condition list -g {resource_group} --policy-name {policyName} -n {match}'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(len(result), 2)

        cmd = 'az network front-door waf-policy rule list -g {resource_group} --policy-name {policyName}'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(len(result), 3)

        cmd = 'az network front-door waf-policy rule delete -g {resource_group} --policy-name {policyName} -n {disabledRateLimit}'.format(**locals())
        result = self.cmd(cmd)

        cmd = 'az network front-door waf-policy rule show -g {resource_group} --policy-name {policyName} -n {rateLimit}'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(result['name'], rateLimit)
        self.assertEqual(result['priority'], 45)
        self.assertEqual(result['action'], "Block")
        self.assertEqual(result['rateLimitDurationInMinutes'], 5)

        cmd = 'az network front-door waf-policy rule list -g {resource_group} --policy-name {policyName}'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(len(result), 2)

    @ResourceGroupPreparer(location='westus', additional_tags={'owner': 'jingnanxu'})
    def test_waf_exclusions(self, resource_group):
        # multi-line comment below
        """
  az network front-door waf-policy managed-rules exclusion add -g {resource_group} --policy-name {policyName} --type {type} --match-variable {match_variable} --operator {operator} --value {value}
  az network front-door waf-policy managed-rules exclusion remove -g {resource_group} --policy-name {policyName} --type {type} --match-variable {match_variable} --operator {operator} --value {value}
  az network front-door waf-policy managed-rules exclusion list -g {resource_group} --policy-name {policyName} --type {type}
  az network front-door waf-policy managed-rules exclusion add -g {resource_group} --policy-name {policyName} --type {type} --rule-group-id {rule_group} --match-variable {match_variable} --operator {operator} --value {value}
  az network front-door waf-policy managed-rules exclusion remove -g {resource_group} --policy-name {policyName} --type {type} --rule-group-id {rule_group} --match-variable {match_variable} --operator {operator} --value {value}
  az network front-door waf-policy managed-rules exclusion list -g {resource_group} --policy-name {policyName} --type {type} --rule-group-id {rule_group}
  az network front-door waf-policy managed-rules exclusion add -g {resource_group} --policy-name {policyName} --type {type} --rule-group-id {rule_group} --rule-id {ruleid} --match-variable {match_variable} --operator {operator} --value {value}
  az network front-door waf-policy managed-rules exclusion remove -g {resource_group} --policy-name {policyName} --type {type} --rule-group-id {rule_group} --rule-id {ruleid} --match-variable {match_variable} --operator {operator} --value {value}
  az network front-door waf-policy managed-rules exclusion list -g {resource_group} --policy-name {policyName} --type {type} --rule-group-id {rule_group} --rule-id {ruleid}
"""
        subscription = self.current_subscription()
        policyName = self.create_random_name(prefix='cli', length=24)
        cmd = 'az network front-door waf-policy create -g {resource_group} -n {policyName} --mode prevention'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(result['name'], policyName)
        self.assertEqual(result['policySettings']['mode'], "Prevention")
        self.assertEqual(result['policySettings']['requestBodyCheck'], "Enabled")
        self.assertIn('customRules', result)
        self.assertIn('managedRules', result)
        self.assertIn('id', result)
        self.assertEqual(result['sku']['name'], "Premium_AzureFrontDoor")

        type = "DefaultRuleSet"
        version = "1.0"
        cmd = 'az network front-door waf-policy managed-rules add -g {resource_group} --policy-name {policyName} --type {type} --version {version}'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertIn('managedRules', result)
        self.assertEqual(result['managedRules']['managedRuleSets'][0]['ruleSetType'], type)

        matchVariable = "RequestHeaderNames"
        op = "Contains"
        selector = "ignoreme"

        cmd = 'az network front-door waf-policy managed-rules exclusion list -g {resource_group} --policy-name {policyName} --type {type}'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(len(result), 0)

        cmd = 'az network front-door waf-policy managed-rules exclusion add -g {resource_group} --policy-name {policyName} --type {type} --match-variable {matchVariable} --operator {op} --value {selector}'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        exclusions = result['managedRules']['managedRuleSets'][0]['exclusions']
        self.assertEqual(exclusions[0]["matchVariable"], matchVariable)
        self.assertEqual(exclusions[0]["selectorMatchOperator"], op)
        self.assertEqual(exclusions[0]["selector"], selector)
        exclusions = None

        cmd = 'az network front-door waf-policy managed-rules exclusion list -g {resource_group} --policy-name {policyName} --type {type}'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        exclusions = result
        self.assertEqual(len(exclusions), 1)
        self.assertEqual(exclusions[0]["matchVariable"], matchVariable)
        self.assertEqual(exclusions[0]["selectorMatchOperator"], op)
        self.assertEqual(exclusions[0]["selector"], selector)

        cmd = 'az network front-door waf-policy managed-rules exclusion remove -g {resource_group} --policy-name {policyName} --type {type} --match-variable {matchVariable} --operator {op} --value {selector}'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        exclusions = result['managedRules']['managedRuleSets'][0]['exclusions']
        self.assertEqual(len(exclusions), 0)

        cmd = 'az network front-door waf-policy managed-rules exclusion list -g {resource_group} --policy-name {policyName} --type {type}'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(len(result), 0)

        rulegroupid = "SQLI"
        cmd = 'az network front-door waf-policy managed-rules exclusion list -g {resource_group} --policy-name {policyName} --type {type} --rule-group-id {rulegroupid}'.format(**locals())
        try:
            result = self.cmd(cmd)
            self.fail("should throw exception")
        except CLIError as e:
            self.assertEqual(str(e), "Rule group 'SQLI' not found")

        cmd = 'az network front-door waf-policy managed-rules exclusion add -g {resource_group} --policy-name {policyName} --type {type} --rule-group-id {rulegroupid} --match-variable {matchVariable} --operator {op} --value {selector}'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        ruleGroupOverride = result['managedRules']['managedRuleSets'][0]['ruleGroupOverrides'][0]
        self.assertEqual(rulegroupid, ruleGroupOverride["ruleGroupName"])
        exclusions = ruleGroupOverride['exclusions']
        self.assertEqual(len(exclusions), 1)
        self.assertEqual(exclusions[0]["matchVariable"], matchVariable)
        self.assertEqual(exclusions[0]["selectorMatchOperator"], op)
        self.assertEqual(exclusions[0]["selector"], selector)

        cmd = 'az network front-door waf-policy managed-rules exclusion list -g {resource_group} --policy-name {policyName} --type {type} --rule-group-id {rulegroupid}'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        exclusions = result
        self.assertEqual(len(exclusions), 1)
        self.assertEqual(exclusions[0]["matchVariable"], matchVariable)
        self.assertEqual(exclusions[0]["selectorMatchOperator"], op)
        self.assertEqual(exclusions[0]["selector"], selector)

        cmd = 'az network front-door waf-policy managed-rules exclusion remove -g {resource_group} --policy-name {policyName} --type {type} --rule-group-id {rulegroupid} --match-variable {matchVariable} --operator {op} --value {selector}'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        ruleGroupOverride = result['managedRules']['managedRuleSets'][0]['ruleGroupOverrides'][0]
        self.assertEqual(ruleGroupOverride["ruleGroupName"], rulegroupid)
        exclusions = ruleGroupOverride['exclusions']
        self.assertEqual(len(exclusions), 0)

        ruleid = "942100"
        cmd = 'az network front-door waf-policy managed-rules exclusion list -g {resource_group} --policy-name {policyName} --type {type} --rule-group-id {rulegroupid} --rule-id {ruleid} '.format(**locals())
        try:
            result = self.cmd(cmd)
            self.fail("should throw exception")
        except CLIError as e:
            self.assertEqual(str(e), "Rule '942100' not found")

        cmd = 'az network front-door waf-policy managed-rules exclusion add -g {resource_group} --policy-name {policyName} --type {type} --rule-group-id {rulegroupid}  --rule-id {ruleid} --match-variable {matchVariable} --operator {op} --value {selector}'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        ruleOverride = result['managedRules']['managedRuleSets'][0]['ruleGroupOverrides'][0]["rules"][0]
        self.assertEqual(ruleOverride["ruleId"], ruleid)
        exclusions = ruleOverride['exclusions']
        self.assertEqual(len(exclusions), 1)
        self.assertEqual(exclusions[0]["matchVariable"], matchVariable)
        self.assertEqual(exclusions[0]["selectorMatchOperator"], op)
        self.assertEqual(exclusions[0]["selector"], selector)

        cmd = 'az network front-door waf-policy managed-rules exclusion list -g {resource_group} --policy-name {policyName} --type {type} --rule-group-id {rulegroupid} --rule-id {ruleid} '.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        exclusions = result
        self.assertEqual(len(exclusions), 1)
        self.assertEqual(exclusions[0]["matchVariable"], matchVariable)
        self.assertEqual(exclusions[0]["selectorMatchOperator"], op)
        self.assertEqual(exclusions[0]["selector"], selector)

        cmd = 'az network front-door waf-policy managed-rules exclusion remove -g {resource_group} --policy-name {policyName} --type {type} --rule-group-id {rulegroupid}  --rule-id {ruleid} --match-variable {matchVariable} --operator {op} --value {selector}'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        ruleOverride = result['managedRules']['managedRuleSets'][0]['ruleGroupOverrides'][0]["rules"][0]
        self.assertEqual(ruleOverride["ruleId"], ruleid)
        exclusions = ruleOverride['exclusions']
        self.assertEqual(len(exclusions), 0)

        cmd = 'az network front-door waf-policy managed-rules exclusion list -g {resource_group} --policy-name {policyName} --type {type} --rule-group-id {rulegroupid} --rule-id {ruleid} '.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        exclusions = result
        self.assertEqual(len(exclusions), 0)
