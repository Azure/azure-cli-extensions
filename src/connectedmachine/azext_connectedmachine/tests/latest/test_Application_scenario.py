# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse


class ApplicationScenarioTest(ScenarioTest):
    @AllowLargeResponse(size_kb=9999)
    def test_application(self):
        self.kwargs.update({
            'machine': 'DESKTOP-1NSLNPE',
            'rg': 'vedkale-rg',
            'location': 'centraluseuap',
            'app': 'chrome',
            'package_id': '/subscriptions/{}/resourceGroups/vedkale-rg/providers/Microsoft.Compute/galleries/'
                          'vk_gallery_test/applications/chrome/versions/2.0.0'.format(self.get_subscription_id()),
        })

        self.cmd('az connectedmachine application add '
                 '--name "{app}" '
                 '--machine-name "{machine}" '
                 '--resource-group "{rg}" '
                 '--location "{location}" '
                 '--package-reference-id "{package_id}" '
                 '--order 1',
                 checks=[
                     self.check('name', '{app}'),
                     self.check('properties.provisioningState', 'Succeeded'),
                     self.check('properties.order', 1),
                 ])

        self.cmd('az connectedmachine application wait '
                 '--name "{app}" '
                 '--machine-name "{machine}" '
                 '--resource-group "{rg}" '
                 '--created')

        self.cmd('az connectedmachine application show '
                 '--name "{app}" '
                 '--machine-name "{machine}" '
                 '--resource-group "{rg}"',
                 checks=[
                     self.check('name', '{app}'),
                     self.check('properties.packageReferenceId', '{package_id}', case_sensitive=False),
                 ])

        self.cmd('az connectedmachine application list '
                 '--machine-name "{machine}" '
                 '--resource-group "{rg}"',
                 checks=[
                     self.check("length([?name=='{app}'])", 1),
                 ])

        self.cmd('az connectedmachine application instance show '
                 '--name "{app}" '
                 '--machine-name "{machine}" '
                 '--resource-group "{rg}"',
                 checks=[
                     self.check('name', '{app}'),
                 ])

        self.cmd('az connectedmachine application update '
                 '--name "{app}" '
                 '--machine-name "{machine}" '
                 '--resource-group "{rg}" '
                 '--tags env=test',
                 checks=[
                     self.check('name', '{app}'),
                     self.check('tags.env', 'test'),
                 ])

        self.cmd('az connectedmachine application delete '
                 '--name "{app}" '
                 '--machine-name "{machine}" '
                 '--resource-group "{rg}" '
                 '--yes')
