# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (
    JMESPathCheck,
    NoneCheck,
    ResourceGroupPreparer,
    ScenarioTest)
from .constants import DEFAULT_LOCATION, CLUSTER_NAME_PREFIX, CLUSTER_NAME_MAX_LENGTH, PASSWORD_PREFIX


class HorizonDBClusterMgmtScenarioTest(ScenarioTest):

    location = DEFAULT_LOCATION

    @AllowLargeResponse()
    @ResourceGroupPreparer(location=location)
    def test_horizondb_cluster_mgmt(self, resource_group):
        self._test_horizondb_cluster_mgmt(resource_group)

    def _test_horizondb_cluster_mgmt(self, resource_group):

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

        self.assertEqual(create_result['name'], cluster_name)
        self.assertEqual(create_result['location'], location)

        # Show cluster
        show_result = self.cmd('horizondb show -g {} -n {}'.format(
            resource_group, cluster_name)).get_output_in_json()

        self.assertEqual(show_result['name'], cluster_name)
        self.assertEqual(show_result['properties']['version'], version)
        self.assertEqual(show_result['properties']['vCores'], v_cores)
        self.assertEqual(show_result['properties']['replicaCount'], replica_count)

        # Run list assertions in live mode so playback remains stable until
        # list interactions are recorded.

        # TODO: Uncomment once cluster list is working. Subscription scoped cluster list currently
        # returns 502 Bad Gateway in live mode, which causes playback to fail since the response is not recorded.
        if self.is_live:
            # List clusters in the resource group and ensure the cluster is returned
            self.cmd('horizondb list -g {}'.format(resource_group),
                        checks=[JMESPathCheck("[?name=='{}'] | length(@)".format(cluster_name), 1)])

        #     # List clusters in subscription scope and ensure the cluster is returned
        #     self.cmd('horizondb list',
        #              checks=[JMESPathCheck("[?name=='{}'] | length(@)".format(cluster_name), 1)])

        # Update cluster
        v_cores_update = v_cores - 2
        show_result = self.cmd('horizondb update -g {} -n {} --v-cores {}'.format(
            resource_group, cluster_name, v_cores_update)).get_output_in_json()

        self.assertEqual(show_result['properties']['vCores'], v_cores_update)

        from datetime import datetime, timedelta, timezone

        restored_cluster_name = self.create_random_name(CLUSTER_NAME_PREFIX, CLUSTER_NAME_MAX_LENGTH)

        # Restore time must be at least 5 minutes (300s) before the current time during preview.
        # Playback matches on method + URI only (not request body), so this value is not
        # replay-sensitive; in live runs it must be a recent time within the retention window.
        restore_time = (datetime.now(timezone.utc) - timedelta(minutes=6)).replace(microsecond=0).isoformat()

        # Restore cluster
        restore_result = self.cmd('horizondb restore -g {} -n {} --source-cluster {} --restore-time {}'.format(
            resource_group, restored_cluster_name, cluster_name, restore_time)).get_output_in_json()

        self.assertEqual(restore_result['name'], restored_cluster_name)
        self.assertEqual(restore_result['properties']['createMode'], 'PointInTimeRestore')

        # Delete restored cluster
        self.cmd('horizondb delete -g {} -n {} --yes'.format(resource_group, restored_cluster_name),
                 checks=NoneCheck())

        # Delete cluster
        self.cmd('horizondb delete -g {} -n {} --yes'.format(resource_group, cluster_name),
                 checks=NoneCheck())
