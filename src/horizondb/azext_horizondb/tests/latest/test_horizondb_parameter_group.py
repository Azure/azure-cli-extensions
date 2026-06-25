# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (
    NoneCheck,
    ResourceGroupPreparer,
    ScenarioTest)
from .constants import DEFAULT_LOCATION, CLUSTER_NAME_PREFIX, CLUSTER_NAME_MAX_LENGTH, PASSWORD_PREFIX


class HorizonDBParameterGroupScenarioTest(ScenarioTest):

    location = DEFAULT_LOCATION

    @AllowLargeResponse()
    @ResourceGroupPreparer(location=location)
    def test_horizondb_parameter_group(self, resource_group):
        self._test_horizondb_parameter_group(resource_group)

    def _test_horizondb_parameter_group(self, resource_group):

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
