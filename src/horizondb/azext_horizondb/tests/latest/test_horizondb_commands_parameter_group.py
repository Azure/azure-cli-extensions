# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (
    NoneCheck,
    ResourceGroupPreparer,
    ScenarioTest)
from .constants import (
    DEFAULT_LOCATION,
    CLUSTER_NAME_PREFIX,
    CLUSTER_NAME_MAX_LENGTH,
    PARAMETER_GROUP_NAME_PREFIX,
    PARAMETER_GROUP_NAME_MAX_LENGTH,
    PASSWORD_PREFIX)


class HorizonDBParameterGroupScenarioTest(ScenarioTest):

    location = DEFAULT_LOCATION

    @AllowLargeResponse()
    @ResourceGroupPreparer(location=location)
    def test_horizondb_parameter_group_mgmt(self, resource_group):
        self._test_horizondb_parameter_group_mgmt(resource_group)

    def _test_horizondb_parameter_group_mgmt(self, resource_group):

        location = self.location
        cluster_name = self.create_random_name(CLUSTER_NAME_PREFIX, CLUSTER_NAME_MAX_LENGTH)
        admin_user = 'horizonadmin'
        admin_password = self.create_random_name(PASSWORD_PREFIX, 20)
        version = '17'
        v_cores = 4
        replica_count = 3

        # Create cluster
        create_result = self.cmd('horizondb create -g {} -n {} --location {} '
                                 '--administrator-login {} --administrator-login-password {} '
                                 '--version {} --v-cores {} --replica-count {}'.format(
                                     resource_group, cluster_name, location,
                                     admin_user, admin_password,
                                     version, v_cores, replica_count)).get_output_in_json()

        parameter_group_id = create_result['properties']['parameterGroup']['id']

        # Update cluster
        update_result = self.cmd('horizondb update -g {} -n {} --parameter-group "{}"'.format(
            resource_group, cluster_name, parameter_group_id)).get_output_in_json()

        self.assertEqual(update_result['properties']['parameterGroup']['id'], parameter_group_id)

        # Delete cluster
        self.cmd('horizondb delete -g {} -n {} --yes'.format(resource_group, cluster_name),
                 checks=NoneCheck())


class HorizonDBParameterGroupCrudScenarioTest(ScenarioTest):

    location = DEFAULT_LOCATION

    @AllowLargeResponse()
    @ResourceGroupPreparer(location=location)
    def test_horizondb_parameter_group_crud(self, resource_group):
        self._test_horizondb_parameter_group_crud(resource_group)

    def _test_horizondb_parameter_group_crud(self, resource_group):

        location = self.location
        parameter_group_name = self.create_random_name(PARAMETER_GROUP_NAME_PREFIX, PARAMETER_GROUP_NAME_MAX_LENGTH)
        pg_version = 17

        # Malformed --parameters value is rejected before any service call
        self.cmd('horizondb parameter-group create -g {} -n {} --location {} '
                 '--version {} --parameters max_connections'.format(
                     resource_group, parameter_group_name, location, pg_version),
                 expect_failure=True)

        # --parameters is required; omitting it fails argument validation before any service call
        with self.assertRaises(SystemExit):
            self.cmd('horizondb parameter-group create -g {} -n {} --location {} --version {}'.format(
                resource_group, parameter_group_name, location, pg_version))

        # Create parameter group with custom parameters
        self.cmd('horizondb parameter-group create -g {} -n {} --location {} '
                 '--version {} --parameters max_connections=200 work_mem=8192 '
                 '--apply-immediately true --tags env=test '
                 '--description "Initial description"'.format(
                     resource_group, parameter_group_name, location, pg_version),
                 checks=[
                     self.check('name', parameter_group_name),
                     self.check('properties.description', 'Initial description'),
                     self.check('properties.pgVersion', pg_version),
                     self.check('tags.env', 'test'),
                     self.check("length(properties.parameters[?name=='max_connections' && value=='200'])", 1),
                     self.check("length(properties.parameters[?name=='work_mem' && value=='8192'])", 1),
                 ])

        # Show parameter group
        self.cmd('horizondb parameter-group show -g {} -n {}'.format(resource_group, parameter_group_name),
                 checks=[
                     self.check('name', parameter_group_name),
                     self.check('properties.pgVersion', pg_version),
                     self.check('tags.env', 'test'),
                     self.check("length(properties.parameters[?name=='max_connections' && value=='200'])", 1),
                 ])

        # List parameter groups in the resource group
        self.cmd('horizondb parameter-group list -g {}'.format(resource_group),
                 checks=[
                     self.check("length([?name=='{}'])".format(parameter_group_name), 1),
                 ])

        # List parameter groups in the subscription (no resource group filter)
        self.cmd('horizondb parameter-group list',
                 checks=[
                     self.check("length([?name=='{}'])".format(parameter_group_name), 1),
                 ])

        # Delete parameter group
        self.cmd('horizondb parameter-group delete -g {} -n {} --yes'.format(resource_group, parameter_group_name),
                 checks=NoneCheck())

        # Listing the resource group no longer returns the deleted group
        self.cmd('horizondb parameter-group list -g {}'.format(resource_group),
                 checks=[
                     self.check("length([?name=='{}'])".format(parameter_group_name), 0),
                 ])
