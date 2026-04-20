# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import *  # pylint: disable=unused-import


class ServiceGroupScenarioTest(ScenarioTest):

    @record_only()
    def test_servicegroup_crud(self):
        """Test create, show, update, and delete of a service group."""
        self.kwargs.update({
            'name': self.create_random_name('sg-test-', 24),
            'display_name': 'Test Service Group',
            'updated_display_name': 'Updated Service Group',
        })

        # Create a service group
        self.cmd(
            'az service-group create --name {name} --display-name "{display_name}"',
            checks=[
                self.check('name', '{name}'),
                self.check('displayName', '{display_name}'),
                self.check('provisioningState', 'Succeeded'),
            ]
        )

        # Show the service group
        self.cmd(
            'az service-group show --name {name}',
            checks=[
                self.check('name', '{name}'),
                self.check('displayName', '{display_name}'),
            ]
        )

        # Update the service group
        self.cmd(
            'az service-group update --name {name} --display-name "{updated_display_name}"',
            checks=[
                self.check('name', '{name}'),
                self.check('displayName', '{updated_display_name}'),
            ]
        )

        # Delete the service group
        self.cmd('az service-group delete --name {name} --yes')

    @record_only()
    def test_servicegroup_list_ancestors(self):
        """Test listing ancestors of a service group with parent-child hierarchy."""
        self.kwargs.update({
            'parent_name': self.create_random_name('sg-parent-', 24),
            'child_name': self.create_random_name('sg-child-', 24),
        })

        # Create parent service group
        self.cmd(
            'az service-group create --name {parent_name} --display-name "Parent Group"',
            checks=[
                self.check('provisioningState', 'Succeeded'),
            ]
        )

        # Create child with parent reference
        self.cmd(
            'az service-group create --name {child_name} --display-name "Child Group" '
            '--parent resource-id="/providers/Microsoft.Management/serviceGroups/{parent_name}"',
            checks=[
                self.check('provisioningState', 'Succeeded'),
            ]
        )

        # List ancestors of child — should include parent
        result = self.cmd(
            'az service-group list-ancestors --name {child_name}'
        ).get_output_in_json()

        self.assertIsInstance(result, dict)
        self.assertIn('value', result)
        ancestor_ids = [a.get('id', '') for a in result.get('value', [])]
        self.assertTrue(
            any(self.kwargs['parent_name'] in aid for aid in ancestor_ids),
            f"Expected parent '{self.kwargs['parent_name']}' in ancestors: {ancestor_ids}"
        )

        # Clean up
        self.cmd('az service-group delete --name {child_name} --yes')
        self.cmd('az service-group delete --name {parent_name} --yes')

    @record_only()
    def test_servicegroup_create_with_parent(self):
        """Test creating a service group with a parent."""
        self.kwargs.update({
            'parent_name': self.create_random_name('sg-par-', 24),
            'child_name': self.create_random_name('sg-chl-', 24),
        })

        # Create parent service group
        self.cmd(
            'az service-group create --name {parent_name} --display-name "Parent Group"',
            checks=[
                self.check('name', '{parent_name}'),
                self.check('provisioningState', 'Succeeded'),
            ]
        )

        # Create child service group with parent
        self.cmd(
            'az service-group create --name {child_name} --display-name "Child Group" '
            '--parent resource-id="/providers/Microsoft.Management/serviceGroups/{parent_name}"',
            checks=[
                self.check('name', '{child_name}'),
                self.check('parent.resourceId',
                           '/providers/Microsoft.Management/serviceGroups/{parent_name}'),
                self.check('provisioningState', 'Succeeded'),
            ]
        )

        # Clean up
        self.cmd('az service-group delete --name {child_name} --yes')
        self.cmd('az service-group delete --name {parent_name} --yes')
