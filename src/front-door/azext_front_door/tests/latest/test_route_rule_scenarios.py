# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


class RouteRuleScenarioTests(ScenarioTest):

    @ResourceGroupPreparer(location='westus')
    def test_route_rule_basic(self, resource_group):
        self.kwargs.update({
            'front_door': self.create_random_name('clifrontdoor', 20),
            'rule1': 'rule1',
            'rule2': 'rule2'
        })
        self.cmd('network front-door create -g {rg} -n {front_door} --backend-address 202.120.2.3')
        self.cmd('network front-door routing-rule create -f {front_door} -g {rg} -n {rule1} '
                 '--frontend-endpoints DefaultFrontendEndpoint --route-type Forward '
                 '--backend-pool DefaultBackendPool --patterns /forward1')
        self.cmd('network front-door routing-rule update -f {front_door} -g {rg} -n {rule1} '
                 '--patterns /forward2 --caching Disabled',
                 checks=[
                     self.check('patternsToMatch[0]', '/forward2'),
                     self.check('contains(keys(routeConfiguration), "cacheConfiguration")', False)
                 ])
        self.cmd('network front-door routing-rule create -f {front_door} -g {rg} -n {rule2} '
                 '--frontend-endpoints DefaultFrontendEndpoint --route-type Redirect '
                 '--custom-host redirecthost.com --patterns /redirect1 --custom-query-string querystring')
        self.cmd('network front-door routing-rule update -f {front_door} -g {rg} -n {rule2} '
                 '--patterns /forward3 --custom-query-string querystring2',
                 checks=[
                     self.check('patternsToMatch[0]', '/forward3'),
                     self.check('routeConfiguration.customQueryString', 'querystring2')
                 ])
