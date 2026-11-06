# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk import ResourceGroupPreparer, ScenarioTest


class NetworksecurityScenario(ScenarioTest):

    @ResourceGroupPreparer(location='westus', subscription=os.environ.get('AZURE_TEST_SUBSCRIPTION_ID'))
    def test_neuroshield_lifecycle(self, resource_group):
        if self.in_recording:
            # Keep dev resource-group overrides sanitized and replayable.
            for preparer in self.recording_processors:
                if isinstance(preparer, ResourceGroupPreparer):
                    self.name_replacer.register_name_pair(resource_group, preparer.moniker)
        self.kwargs.update(
            rg=resource_group,
            name=self.create_random_name('clitestns', 24),
            location='westus',
            subscription=(os.environ.get('AZURE_TEST_SUBSCRIPTION_ID') if self.in_recording else None)
            or self.get_subscription_id()
        )
        created = True
        try:
            resource = self.cmd(
                'networksecurity neuroshield create --subscription {subscription} -g {rg} -n {name} -l {location} '
                '--response-mode Manual --severity-threshold Medium --tags purpose=cli-test',
                checks=[
                    self.check('properties.responseMode', 'Manual'),
                    self.check('properties.severityThreshold', 'Medium'),
                    self.check('tags.purpose', 'cli-test')
                ]
            ).get_output_in_json()
            self.kwargs['id'] = resource['id']
            self.cmd(
                'networksecurity neuroshield show --ids {id}',
                checks=self.check('name', '{name}')
            )
            self.cmd(
                'networksecurity neuroshield create --subscription {subscription} -g {rg} -n {name} -l {location} '
                '--response-mode Manual --severity-threshold High --tags purpose=cli-test',
                checks=self.check('properties.severityThreshold', 'High')
            )
            self.cmd(
                'networksecurity neuroshield update --subscription {subscription} -g {rg} -n {name} '
                '--description "Partial update regression"',
                checks=[
                    self.check('properties.description', 'Partial update regression'),
                    self.check('properties.responseMode', 'Manual'),
                    self.check('properties.severityThreshold', 'High'),
                    self.check('tags.purpose', 'cli-test')
                ]
            )
            self.cmd(
                'networksecurity neuroshield show --subscription {subscription} -g {rg} -n {name}',
                checks=self.check('properties.description', 'Partial update regression')
            )
            self.cmd('networksecurity neuroshield delete --subscription {subscription} -g {rg} -n {name} --yes')
            created = False
            self.cmd('networksecurity neuroshield show --subscription {subscription} -g {rg} -n {name}', expect_failure=True)
        finally:
            if created:
                self.cmd('networksecurity neuroshield delete --subscription {subscription} -g {rg} -n {name} --yes')
