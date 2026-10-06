# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import *  # pylint: disable=unused-import


class ServiceGroupScenarioTest(ScenarioTest):
    """Scenario tests for the service-group CLI extension.

    Service Groups are tenant-scoped hierarchical resources. Creating a new
    service group requires a parent, while updating an existing service group
    does not. The root service group is auto-created by the service when
    referenced as a parent; its ID is the tenant ID:
        /providers/Microsoft.Management/serviceGroups/{tenantId}

    These tests require:
    - The Service Groups API (2026-08-01) available in the tenant
    - Authorization to manage child service groups beneath the tenant root service group
    """

    def _get_root_parent(self):
        """Return the root service group resource ID (tenantId-based)."""
        tenant_id = self.cmd('az account show').get_output_in_json()['tenantId']
        return f'/providers/Microsoft.Management/serviceGroups/{tenant_id}'

    def test_servicegroup_crud(self):
        """Test full CRUD lifecycle: create, show, update, delete a service group under root."""
        root_parent = self._get_root_parent()
        self.kwargs.update({
            'name': self.create_random_name('sg-test-', 24),
            'display_name': 'Test Service Group',
            'updated_display_name': 'Updated Service Group',
            'criticality': 1,
            'expected_criticality': 1.0,
            'updated_criticality': 2,
            'expected_updated_criticality': 2.0,
            'root_parent': root_parent,
        })

        # A new service group requires a parent; an update through the same PUT operation does not.
        self.cmd(
            'az service-group create --name {name} --display-name "{display_name}" '
            '--attributes criticality={criticality} --parent resource-id="{root_parent}"',
            checks=[
                self.check('name', '{name}'),
                self.check('displayName', '{display_name}'),
                self.check('attributes.criticality', '{expected_criticality}'),
                self.check('provisioningState', 'Succeeded'),
                self.check('parent.resourceId', '{root_parent}'),
            ]
        )

        # Show the service group
        self.cmd(
            'az service-group show --name {name}',
            checks=[
                self.check('name', '{name}'),
                self.check('displayName', '{display_name}'),
                self.check('parent.resourceId', '{root_parent}'),
            ]
        )

        # Update the service group display name, criticality, and tags
        self.cmd(
            'az service-group update --name {name} --display-name "{updated_display_name}" '
            '--attributes criticality={updated_criticality} --tags env=test team=cli',
            checks=[
                self.check('name', '{name}'),
                self.check('displayName', '{updated_display_name}'),
                self.check('attributes.criticality', '{expected_updated_criticality}'),
                self.check('tags.env', 'test'),
                self.check('tags.team', 'cli'),
            ]
        )

        # Delete the service group
        self.cmd('az service-group delete --name {name} --yes')

    def test_servicegroup_create_with_nested_parent(self):
        """Test creating a 3-level hierarchy and verify its parent references."""
        root_parent = self._get_root_parent()
        self.kwargs.update({
            'parent_name': self.create_random_name('sg-par-', 24),
            'child_name': self.create_random_name('sg-chl-', 24),
            'root_parent': root_parent,
        })

        # Create parent service group under root
        self.cmd(
            'az service-group create --name {parent_name} --display-name "Parent Group" '
            '--parent resource-id="{root_parent}"',
            checks=[
                self.check('name', '{parent_name}'),
                self.check('provisioningState', 'Succeeded'),
                self.check('parent.resourceId', '{root_parent}'),
            ]
        )

        # Create child service group under parent
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

        # Verify child's parent reference via show
        self.cmd(
            'az service-group show --name {child_name}',
            checks=[
                self.check('parent.resourceId',
                           '/providers/Microsoft.Management/serviceGroups/{parent_name}'),
            ]
        )

        # Clean up (child first, then parent)
        self.cmd('az service-group delete --name {child_name} --yes')
        self.cmd('az service-group delete --name {parent_name} --yes')
