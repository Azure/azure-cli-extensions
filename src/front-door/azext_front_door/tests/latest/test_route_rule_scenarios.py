# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


class RouteRuleScenarioTests(ScenarioTest):

    @ResourceGroupPreparer(location='westus', additional_tags={'owner': 'jingnanxu'})
    def test_route_rule_basic(self, resource_group):
        self.kwargs.update({
            'front_door': self.create_random_name('clifrontdoor', 20),
            'rule1': 'rule1',
            'rule2': 'rule2',
            'rule3': 'rule3',
            'rules_engine': self.create_random_name('rule', 20),
            'ruleengine1': 'ruleengine1'
        })
        self.cmd('network front-door create -g {rg} -n {front_door} --backend-address 202.120.2.3')
        self.cmd('network front-door routing-rule create -f {front_door} -g {rg} -n {rule1} '
                 '--frontend-endpoints DefaultFrontendEndpoint --route-type Forward '
                 '--backend-pool DefaultBackendPool --patterns /forward1')
        self.cmd('network front-door routing-rule update -f {front_door} -g {rg} -n {rule1} '
                 '--patterns /forward2 --caching Enabled',
                 checks=[
                     self.check('patternsToMatch[0]', '/forward2'),
                     self.check('length(routeConfiguration.cacheConfiguration)', 4),
                     self.check('routeConfiguration.cacheConfiguration.queryParameterStripDirective', 'StripNone'),
                     self.check('routeConfiguration.cacheConfiguration.dynamicCompression', 'Enabled')
                 ])
        self.cmd('network front-door routing-rule create -f {front_door} -g {rg} -n {rule2} '
                 '--frontend-endpoints DefaultFrontendEndpoint --route-type Redirect '
                 '--custom-host redirecthost.com --patterns /redirect1 --custom-query-string querystring')
        self.cmd('network front-door routing-rule update -f {front_door} -g {rg} -n {rule2} '
                 '--patterns /forward3 --custom-query-string querystring2 ',
                 checks=[
                     self.check('patternsToMatch[0]', '/forward3'),
                     self.check('routeConfiguration.customQueryString', 'querystring2')
                 ])
        
        # Check rule engine update
        self.cmd('network front-door routing-rule create -f {front_door} -g {rg} -n {rule3} '
                 '--frontend-endpoints DefaultFrontendEndpoint --route-type Forward '
                 '--patterns /forward4 --backend-pool DefaultBackendPool '
                 '--caching Enabled --query-parameter-strip-directive StripAllExcept --query-parameters ak=1,sk=2 '
                 '--cache-duration P1DT1H1M1S')

        self.cmd('network front-door routing-rule update -f {front_door} -g {rg} -n {rule3} '
                 '--patterns /forward5 /forward4',
                 checks=[
                     self.check('patternsToMatch[0]', '/forward5'),
                     self.check('patternsToMatch[1]', '/forward4'),
                     self.check('routeConfiguration.cacheConfiguration.queryParameterStripDirective', 'StripAllExcept'),
                     self.check('routeConfiguration.cacheConfiguration.queryParameters', 'ak=1,sk=2'),
                     self.check('routeConfiguration.cacheConfiguration.dynamicCompression', 'Enabled')
                 ])

        # Create a rule engine
        rule_engine_id = self.cmd('network front-door rules-engine rule create -f {front_door} -g {rg} '
                                '--rules-engine-name {rules_engine} --name {ruleengine1} --priority 1 '
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
                                ]).get_output_in_json()["id"]

        # Update rule enginer configuration for routing rule.
        # Other properties should not be changed by accident.
        self.cmd(f'network front-door routing-rule update -f {self.kwargs["front_door"]} -g {self.kwargs["rg"]} -n {self.kwargs["rule3"]} '
                 f'--rules-engine {rule_engine_id}',
                 checks=[
                     self.check('patternsToMatch[0]', '/forward5'),
                     self.check('patternsToMatch[1]', '/forward4'),
                     self.check('rulesEngine.id', rule_engine_id),
                     self.check('routeConfiguration.cacheConfiguration.queryParameterStripDirective', 'StripAllExcept'),
                     self.check('routeConfiguration.cacheConfiguration.queryParameters', 'ak=1,sk=2'),
                     self.check('routeConfiguration.cacheConfiguration.dynamicCompression', 'Enabled')
                 ])

        # Caching configuration field should also be able to be updated individually
        self.cmd('network front-door routing-rule update -f {front_door} -g {rg} -n {rule3} '
                 '--query-parameters ak=2,sk=3',
                 checks=[
                     self.check('patternsToMatch[0]', '/forward5'),
                     self.check('patternsToMatch[1]', '/forward4'),
                     self.check('rulesEngine.id', rule_engine_id),
                     self.check('routeConfiguration.cacheConfiguration.queryParameterStripDirective', 'StripAllExcept'),
                     self.check('routeConfiguration.cacheConfiguration.queryParameters', 'ak=2,sk=3'),
                     self.check('routeConfiguration.cacheConfiguration.dynamicCompression', 'Enabled')
                 ])

        # Dissociate rule enginer with routing rule
        self.cmd('network front-door routing-rule update -f {front_door} -g {rg} -n {rule3} '
                 '--remove rulesEngine --dynamic-compression Disabled',
                 checks=[
                     self.check('patternsToMatch[0]', '/forward5'),
                     self.check('patternsToMatch[1]', '/forward4'),
                     self.check('rulesEngine', None),
                     self.check('routeConfiguration.cacheConfiguration.queryParameterStripDirective', 'StripAllExcept'),
                     self.check('routeConfiguration.cacheConfiguration.queryParameters', 'ak=2,sk=3'),
                     self.check('routeConfiguration.cacheConfiguration.dynamicCompression', 'Disabled')
                 ])

        # Default routing rule should also be counted
        self.cmd('network front-door routing-rule list -f {front_door} -g {rg} ',
                 checks=[
                     self.check('length(@)', 4),
                 ])

        self.cmd('network front-door routing-rule delete -f {front_door} -g {rg} -n {rule3} ')
        self.cmd('network front-door routing-rule delete -f {front_door} -g {rg} -n {rule2} ')
        self.cmd('network front-door routing-rule list -f {front_door} -g {rg} ',
                 checks=[
                     self.check('length(@)', 2),
                 ])
        self.cmd('network front-door routing-rule show -f {front_door} -g {rg} -n {rule1} ')
