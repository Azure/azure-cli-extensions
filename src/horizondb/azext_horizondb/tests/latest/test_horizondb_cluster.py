# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import NoneCheck, ResourceGroupPreparer, ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

from .constants import JAPANEAST, CLUSTER_NAME_PREFIX, CLUSTER_NAME_MAX_LENGTH


class HorizonDBClusterMgmtScenarioTest(ScenarioTest):

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_horizondb_cluster_', location=JAPANEAST)
    def test_horizondb_cluster_mgmt(self, resource_group):
        self.kwargs.update({
            'rg': resource_group,
            'location': JAPANEAST,
            'cluster': self.create_random_name(CLUSTER_NAME_PREFIX, CLUSTER_NAME_MAX_LENGTH),
        })

        cluster = self.cmd(
            'horizondb cluster create -g {rg} -n {cluster} --location {location} '
            '--version 17 --geo-redundancy Disabled --public-access Disabled --tags scenario=cluster',
            checks=[
                self.check('name', '{cluster}'),
                self.check('location', '{location}'),
                self.check('properties.postgreSqlVersion', '17'),
                self.check('properties.provisioningState', 'Succeeded'),
            ],
        ).get_output_in_json()
        self.kwargs['source_id'] = cluster['id']

        self.cmd('horizondb cluster show -g {rg} -n {cluster}', checks=[
            self.check('id', '{source_id}'),
            self.check('properties.backup.geoRedundancy', 'Disabled'),
            self.check('properties.network.publicAccess', 'Disabled'),
            self.check('tags.scenario', 'cluster'),
        ])
        self.cmd('horizondb cluster list -g {rg}', checks=[
            self.check("[?name=='{cluster}'] | length(@)", 1),
        ])
        self.cmd(
            'horizondb cluster update -g {rg} -n {cluster} '
            '--backup-retention-days 9',
            checks=[
                self.check('properties.backup.retentionDays', 9),
            ],
        )

        self.cmd('horizondb cluster delete -g {rg} -n {cluster} --yes', checks=NoneCheck())
        self.cmd('horizondb cluster list -g {rg}', checks=self.check('length(@)', 0))
