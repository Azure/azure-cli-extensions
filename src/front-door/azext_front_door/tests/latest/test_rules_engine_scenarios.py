# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


class RulesEngineScenarioTests(ScenarioTest):

    @ResourceGroupPreparer(location='westus')
    def test_rules_engine_basic(self, resource_group):
        self.kwargs.update({
            'front_door': self.create_random_name('clifrontdoor', 20),
            'rules_engine': self.create_random_name('clirulesengine', length=20),
            'rule1': 'rule1',
            'rule2': 'rule2'
        })

        """Step 1: Create a Front Door"""
        self.cmd('network front-door create -g {rg} -n {front_door} --backend-address 202.120.2.3')

        """Step 2: Create a Rules Engine configuration with one rule in the Front Door"""
        self.cmd('network front-door rules-engine rule create -n {front_door} -g {rg} '
                 '--rules-engine-name {rules_engine} --rule-name {rule1} --priority 1 '
                 '--action-type RequestHeader --header-action Overwrite --header-name Rewrite '
                 '--header-value True --match-variable RequestFilenameExtension --operator Contains '
                 '--match-values jpg png --transforms Lowercase',
                 checks=[
                     self.check('length(rules)', 1),
                     self.check('length(rules[0].action.requestHeaderActions)', 1),
                     self.check('rules[0].action.requestHeaderActions[0].headerActionType', 'Overwrite'),
                     self.check('rules[0].action.requestHeaderActions[0].headerName', 'Rewrite'),
                     self.check('rules[0].action.requestHeaderActions[0].value', 'True'),
                     self.check('length(rules[0].matchConditions)', 1),
                     self.check('rules[0].matchConditions[0].rulesEngineMatchVariable', 'RequestFilenameExtension'),
                     self.check('rules[0].matchConditions[0].rulesEngineOperator', 'Contains'),
                     self.check('rules[0].matchConditions[0].rulesEngineMatchValue', ['jpg', 'png']),
                     self.check('rules[0].matchConditions[0].negateCondition', False),
                     self.check('rules[0].matchConditions[0].selector', None),
                     self.check('rules[0].matchConditions[0].transforms', ['Lowercase']),
                     self.check('rules[0].matchProcessingBehavior', None),
                     self.check('rules[0].priority', 1)
                 ])

        """Step 3: Create another rule in the Rules Engine configuration"""
        self.cmd('network front-door rules-engine rule create -n {front_door} -g {rg} '
                 '--rules-engine-name {rules_engine} --rule-name {rule2} --priority 2 '
                 '--action-type ResponseHeader --header-action Append --header-name Security '
                 '--header-value Strict --match-variable RequestPath --operator Contains '
                 '--match-values private',
                 checks=[
                     self.check('length(rules)', 2),
                     self.check('length(rules[1].action.responseHeaderActions)', 1),
                     self.check('length(rules[1].matchConditions)', 1),
                     self.check('rules[1].priority', 2)
                 ])

        """Step 4: Update a rule in the Rules Engine configuration"""
        self.cmd('network front-door rules-engine rule update -n {front_door} -g {rg} '
                 '--rules-engine-name {rules_engine} --rule-name {rule1} '
                 '--match-processing-behavior Stop',
                 checks=[
                     self.check('rules[0].matchProcessingBehavior', 'Stop')
                 ])

        """Step 5: GET the Rules Engine configuration with two rules"""
        self.cmd('network front-door rules-engine show -n {front_door} -g {rg} '
                 '--rules-engine-name {rules_engine}',
                 checks=[
                     self.check('length(rules)', 2)
                 ])

        """Step 6: Add a Header action to the rule"""
        self.cmd('network front-door rules-engine rule action add -n {front_door} -g {rg} '
                 '--rules-engine-name {rules_engine} --rule-name {rule2} --action-type '
                 'ResponseHeader --header-action Delete --header-name Location',
                 checks=[
                     self.check('length(rules[1].action.responseHeaderActions)', 2),
                     self.check('rules[1].action.responseHeaderActions[1].headerActionType', 'Delete'),
                     self.check('rules[1].action.responseHeaderActions[1].headerName', 'Location'),
                     self.check('rules[1].action.responseHeaderActions[1].value', None)
                 ])

        """Step 7: Add a Forward Route Override action to the rule"""
        self.cmd('network front-door rules-engine rule action add -n {front_door} -g {rg} '
                 '--rules-engine-name {rules_engine} --rule-name {rule1} --action-type '
                 'ForwardRouteOverride --backend-pool DefaultBackendPool --caching Enabled',
                 checks=[
                     self.check('length(rules[0].action.routeConfigurationOverride)', 5),
                     self.check('contains(rules[0].action.routeConfigurationOverride.odatatype, `FrontdoorForwardingConfiguration`)', True),
                     self.check('contains(rules[0].action.routeConfigurationOverride.backendPool.id, `DefaultBackendPool`)', True),
                     self.check('length(rules[0].action.routeConfigurationOverride.cacheConfiguration)', 4)
                 ])

        """Step 8: Add a Redirect Route Override action to the rule"""
        self.cmd('network front-door rules-engine rule action add -n {front_door} -g {rg} '
                 '--rules-engine-name {rules_engine} --rule-name {rule2} --action-type '
                 'RedirectRouteOverride --custom-path /redirect',
                 checks=[
                     self.check('length(rules[1].action.routeConfigurationOverride)', 7),
                     self.check('contains(rules[1].action.routeConfigurationOverride.odatatype, `FrontdoorRedirectConfiguration`)', True),
                     self.check('rules[1].action.routeConfigurationOverride.redirectProtocol', 'MatchRequest'),
                     self.check('rules[1].action.routeConfigurationOverride.customPath', '/redirect')
                 ])

        """Step 9: List all the actions in rule1"""
        self.cmd('network front-door rules-engine rule action list -n {front_door} -g {rg} '
                 '--rules-engine-name {rules_engine} --rule-name {rule1}',
                 checks=[
                     self.check('length(@) > `0`', True)
                 ])

        """Step 10: List all the actions in rule2"""
        self.cmd('network front-door rules-engine rule action list -n {front_door} -g {rg} '
                 '--rules-engine-name {rules_engine} --rule-name {rule2}',
                 checks=[
                     self.check('length(@) > `0`', True)
                 ])

        """Step 11: Add a match condition to the rule"""
        self.cmd('network front-door rules-engine rule condition add -n {front_door} -g {rg} '
                 '--rules-engine-name {rules_engine} --rule-name {rule1} --match-variable '
                 'RequestHeader --selector x-language --operator Equal '
                 '--match-values en-gb en-th --transforms Lowercase',
                 checks=[
                     self.check('length(rules[0].matchConditions)', 2),
                     self.check('rules[0].matchConditions[1].rulesEngineMatchVariable', 'RequestHeader'),
                     self.check('rules[0].matchConditions[1].rulesEngineOperator', 'Equal'),
                     self.check('rules[0].matchConditions[1].rulesEngineMatchValue', ['en-gb', 'en-th']),
                     self.check('rules[0].matchConditions[1].negateCondition', False),
                     self.check('rules[0].matchConditions[1].selector', 'x-language'),
                     self.check('rules[0].matchConditions[1].transforms', ['Lowercase'])
                 ])

        """Step 12: List all the match conditions in a rule"""
        self.cmd('network front-door rules-engine rule condition list -n {front_door} -g {rg} '
                 '--rules-engine-name {rules_engine} --rule-name {rule1}',
                 checks=[
                     self.check('length(@)', 2)
                 ])

        """Step 13: Remove a match condition from a rule"""
        self.cmd('network front-door rules-engine rule condition remove -n {front_door} -g {rg} '
                 '--rules-engine-name {rules_engine} --rule-name {rule1} --index 0',
                 checks=[
                     self.check('length(rules[0].matchConditions)', 1)
                 ])

        """Step 14: Remove a Route Override action from a rule"""
        self.cmd('network front-door rules-engine rule action remove -n {front_door} -g {rg} '
                 '--rules-engine-name {rules_engine} --rule-name {rule1} --action-type '
                 'ForwardRouteOverride',
                 checks=[
                     self.check('rules[0].routeConfigurationOverride', None)
                 ])

        """Step 14: Remove a Header action from a rule"""
        self.cmd('network front-door rules-engine rule action remove -n {front_door} -g {rg} '
                 '--rules-engine-name {rules_engine} --rule-name {rule2} --action-type '
                 'ResponseHeader --index 1',
                 checks=[
                     self.check('length(rules[1].action.responseHeaderActions)', 1)
                 ])

        """Step 15: Delete a rule from a Rules Engine configuration"""
        self.cmd('network front-door rules-engine rule delete -n {front_door} -g {rg} '
                 '--rules-engine-name {rules_engine} --rule-name {rule2}',
                 checks=[
                     self.check('length(rules)', 1)
                 ])

        """Step 16: List all the Rules Engine configurations in a Front Door"""
        self.cmd('network front-door rules-engine list -n {front_door} -g {rg}',
                 checks=[
                     self.check('length(@)', 1)
                 ])
