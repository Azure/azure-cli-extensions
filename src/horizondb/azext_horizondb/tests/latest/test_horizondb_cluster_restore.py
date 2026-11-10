# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from datetime import datetime, timedelta, timezone
from time import sleep

from azure.cli.testsdk import NoneCheck, ResourceGroupPreparer, ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk.scenario_tests.const import ENV_LIVE_TEST

from .constants import DEFAULT_LOCATION, CLUSTER_NAME_PREFIX, CLUSTER_NAME_MAX_LENGTH


class HorizonDBClusterRestoreCommandScenarioTest(ScenarioTest):

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_horizondb_restore_', location=DEFAULT_LOCATION)
    def test_horizondb_cluster_restore_command(self, resource_group):
        self.kwargs.update({
            'rg': resource_group,
            'location': DEFAULT_LOCATION,
            'cluster': self.create_random_name(CLUSTER_NAME_PREFIX, CLUSTER_NAME_MAX_LENGTH),
            'restored_cluster': self.create_random_name(CLUSTER_NAME_PREFIX, CLUSTER_NAME_MAX_LENGTH),
            'pool': self.create_random_name('pool-', 24),
        })
        source = self.cmd(
            'horizondb cluster create -g {rg} -n {cluster} --location {location} '
            '--version 17 --geo-redundancy Disabled --public-access Disabled --tags scenario=source',
            checks=[
                self.check('name', '{cluster}'),
                self.check('properties.provisioningState', 'Succeeded'),
            ],
        ).get_output_in_json()
        self.kwargs['source_id'] = source['id']

        self.cmd(
            'horizondb cluster pool create -g {rg} --cluster-name {cluster} -n {pool} '
            '--compute-generation 1 --compute-processor Intel --v-cores 2 '
            '--node-count 1 --high-availability-mode Disabled',
        )
        # Wait until snapshot is created
        os.environ.get(ENV_LIVE_TEST, False) and sleep(1800)
        source = self.cmd('horizondb cluster show -g {rg} -n {cluster}').get_output_in_json()
        self.kwargs['restore_time'] = (
            (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat().replace('+00:00', 'Z')
        )

        self.cmd(
            'horizondb cluster restore -g {rg} -n {restored_cluster} '
            '--source-cluster-id {source_id} --point-in-time-utc {restore_time} --tags scenario=restored',
            checks=[
                self.check('name', '{restored_cluster}'),
                self.check('location', '{location}'),
                self.check('properties.creationMode', 'PointInTimeRestore'),
                self.check('properties.postgreSqlVersion', '17'),
                self.check('properties.backup.geoRedundancy', 'Disabled'),
                self.check('tags.scenario', 'restored'),
            ],
        )

        self.cmd('horizondb cluster delete -g {rg} -n {restored_cluster} --yes', checks=NoneCheck())
        self.cmd(
            'horizondb cluster pool delete -g {rg} --cluster-name {cluster} -n {pool} --yes',
            checks=NoneCheck(),
        )
        self.cmd('horizondb cluster delete -g {rg} -n {cluster} --yes', checks=NoneCheck())
