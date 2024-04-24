# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import requests

from azure.cli.testsdk.scenario_tests import AllowLargeResponse, live_only
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck)
from azure.cli.testsdk.checkers import StringContainCheckIgnoreCase, JMESPathCheckExists, JMESPathCheckNotExists

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


# not lima-specific
class WebappBasicE2EKubeTest(ScenarioTest):
    @ResourceGroupPreparer(location='canadacentral')
    @live_only()
    def test_linux_webapp_quick_create_kube(self, resource_group):
        webapp_name = self.create_random_name(
            prefix='webapp-quick-linux', length=24)
        plan = self.create_random_name(prefix='plan-quick-linux', length=24)

        self.cmd(
            'appservice plan create -g {} -n {} --is-linux'.format(resource_group, plan))
        self.cmd('webapp create -g {} -n {} --plan {} -i patle/ruby-hello'.format(
            resource_group, webapp_name, plan))
        r = requests.get(
            'http://{}.azurewebsites.net'.format(webapp_name), timeout=240)
        # verify the web page
        self.assertTrue('Ruby on Rails in Web Apps on Linux' in str(r.content))
        # verify app settings
        self.cmd('webapp config appsettings list -g {} -n {}'.format(resource_group, webapp_name), checks=[
            JMESPathCheck('[0].name', 'WEBSITES_ENABLE_APP_SERVICE_STORAGE'),
            JMESPathCheck('[0].value', 'false'),
        ])

        self.cmd('webapp update -g {} -n {} --https-only true'.format(resource_group, webapp_name), checks=[JMESPathCheck("httpsOnly", True)])
        self.cmd('webapp update -g {} -n {} --https-only false'.format(resource_group, webapp_name), checks=[JMESPathCheck("httpsOnly", False)])

    @ResourceGroupPreparer(location="eastus")
    def test_win_webapp_quick_create_kube(self, resource_group):
        webapp_name = self.create_random_name(prefix='webapp-quick', length=24)
        plan = self.create_random_name(prefix='plan-quick', length=24)
        self.cmd('appservice plan create -g {} -n {}'.format(resource_group, plan))
        r = self.cmd('webapp create -g {} -n {} --plan {} --deployment-local-git'.format(
            resource_group, webapp_name, plan)).get_output_in_json()
        self.assertTrue(r['ftpPublishingUrl'].startswith('ftps://'))
        self.cmd('webapp config appsettings list -g {} -n {}'.format(resource_group, webapp_name), checks=[
            JMESPathCheck('[0].name', 'WEBSITE_NODE_DEFAULT_VERSION'),
            JMESPathCheck('[0].value', '~16'),
        ])

        self.cmd('webapp update -g {} -n {} --https-only true'.format(resource_group, webapp_name), checks=[JMESPathCheck("httpsOnly", True)])
        self.cmd('webapp update -g {} -n {} --https-only false'.format(resource_group, webapp_name), checks=[JMESPathCheck("httpsOnly", False)])

    @ResourceGroupPreparer(name_prefix="clitest", random_name_length=24, location="eastus")
    def test_win_webapp_quick_create_runtime_kube(self, resource_group):
        webapp_name = self.create_random_name(prefix='webapp-quick', length=24)
        webapp_name_2 = self.create_random_name(prefix='webapp-quick', length=24)
        plan = self.create_random_name(prefix='plan-quick', length=24)
        self.cmd('appservice plan create -g {} -n {}'.format(resource_group, plan))
        r = self.cmd('webapp create -g {} -n {} --plan {} --deployment-local-git -r "node|20LTS"'.format(
            resource_group, webapp_name, plan)).get_output_in_json()
        self.assertTrue(r['ftpPublishingUrl'].startswith('ftps://'))
        self.cmd('webapp config appsettings list -g {} -n {}'.format(resource_group, webapp_name), checks=[
            JMESPathCheck('[0].name', 'WEBSITE_NODE_DEFAULT_VERSION'),
            JMESPathCheck('[0].value', '~20'),
        ])
        r = self.cmd('webapp create -g {} -n {} --plan {} --deployment-local-git -r "dotnet:7"'.format(
            resource_group, webapp_name_2, plan)).get_output_in_json()
        self.assertTrue(r['ftpPublishingUrl'].startswith('ftps://'))

        self.cmd('webapp update -g {} -n {} --https-only true'.format(resource_group, webapp_name), checks=[JMESPathCheck("httpsOnly", True)])
        self.cmd('webapp update -g {} -n {} --https-only false'.format(resource_group, webapp_name), checks=[JMESPathCheck("httpsOnly", False)])

    @ResourceGroupPreparer(name_prefix="clitest", random_name_length=24, location="eastus")
    def test_list_runtimes(self, resource_group):
        r = self.cmd('webapp list-runtimes', checks=[JMESPathCheckExists("linux"), JMESPathCheckExists("windows"),
                                                     StringContainCheckIgnoreCase('NODE:20-lts')]).get_output_in_json()
        self.assertFalse('NODE:14-lts' in r['linux'])
        r = self.cmd('webapp list-runtimes --is-kube',
                     checks=[JMESPathCheckNotExists("linux"), StringContainCheckIgnoreCase('NODE:14-lts')])\
            .get_output_in_json()
        self.assertFalse('NODE:20-lts' in r)
