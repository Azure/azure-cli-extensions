# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


class FleetManagedNamespaceScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli-fleet-ns-', random_name_length=24)
    def test_fleet_managed_namespace_operations(self):
        """Test basic managed namespace operations"""
        
        self.kwargs.update({
            'fleet_name': self.create_random_name('fleet', 10),
            'managed_namespace_name': self.create_random_name('ns', 10),
            'namespace_name': 'test-namespace',
            'location': 'eastus'
        })

        # Create a fleet first
        self.cmd('az fleet create -g {rg} -n {fleet_name} -l {location}', checks=[
            self.check('name', '{fleet_name}'),
            self.check('location', '{location}'),
            self.check('provisioningState', 'Succeeded')
        ])

        # Create a managed namespace
        self.cmd('az fleet managednamespace create -g {rg} -f {fleet_name} -n {managed_namespace_name} --namespace-name {namespace_name}', checks=[
            self.check('name', '{managed_namespace_name}'),
            self.check('namespaceName', '{namespace_name}')
        ])

        # List managed namespaces
        self.cmd('az fleet managednamespace list -g {rg} -f {fleet_name}', checks=[
            self.check('length(@)', 1),
            self.check('[0].name', '{managed_namespace_name}')
        ])

        # Show managed namespace
        self.cmd('az fleet managednamespace show -g {rg} -f {fleet_name} -n {managed_namespace_name}', checks=[
            self.check('name', '{managed_namespace_name}'),
            self.check('namespaceName', '{namespace_name}')
        ])

        # Update managed namespace
        self.cmd('az fleet managednamespace update -g {rg} -f {fleet_name} -n {managed_namespace_name} --labels env=test', checks=[
            self.check('name', '{managed_namespace_name}'),
            self.check('labels.env', 'test')
        ])

        # Delete managed namespace
        self.cmd('az fleet managednamespace delete -g {rg} -f {fleet_name} -n {managed_namespace_name} --yes')

        # Verify deletion
        self.cmd('az fleet managednamespace list -g {rg} -f {fleet_name}', checks=[
            self.check('length(@)', 0)
        ])

        # Clean up fleet
        self.cmd('az fleet delete -g {rg} -n {fleet_name} --yes')