# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from datetime import datetime
import datetime

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class Cosmosdb_previewInAccountRestoreScenarioTest_Table_Gremlin(ScenarioTest):

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_gremlin_database')
    def test_cosmosdb_gremlin_database(self, resource_group):
        db_name = self.create_random_name(prefix='cli', length=15)
        location = "WestUS"

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'db_name': db_name,
            'loc': location
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg} --capabilities EnableGremlin  --backup-policy-type Continuous --locations regionName={loc}')

        assert not self.cmd('az cosmosdb gremlin database exists -g {rg} -a {acc} -n {db_name}').get_output_in_json()

        self.cmd('az cosmosdb gremlin database create -g {rg} -a {acc} -n {db_name}', checks=[
            self.check('name', db_name)
        ]).get_output_in_json()

        self.cmd('az cosmosdb gremlin database show -g {rg} -a {acc} -n {db_name}', checks=[
            self.check('name', db_name)
        ]).get_output_in_json()

        self.cmd('az cosmosdb gremlin database list -g {rg} -a {acc}', checks=[
            self.check('length(@)', 1)
        ]).get_output_in_json()

        assert self.cmd('az cosmosdb gremlin database exists -g {rg} -a {acc} -n {db_name}').get_output_in_json()

        self.cmd('az cosmosdb gremlin database delete -g {rg} -a {acc} -n {db_name} --yes')
        self.cmd('az cosmosdb gremlin database list -g {rg} -a {acc}', checks=[
            self.check('length(@)', 0)
        ]).get_output_in_json()

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_gremlin_graph')
    def test_cosmosdb_gremlin_graph(self, resource_group):
        db_name = self.create_random_name(prefix='cli', length=15)
        gp_name = self.create_random_name(prefix='cli', length=15)
        partition_key = "/thePartitionKey"
        default_ttl = 1000
        new_default_ttl = 2000
        conflict_resolution_policy = '"{\\"mode\\": \\"lastWriterWins\\", \\"conflictResolutionPath\\": \\"/path\\"}"'
        indexing = '"{\\"indexingMode\\": \\"consistent\\", \\"automatic\\": true, \\"includedPaths\\": [{\\"path\\": \\"/*\\"}], \\"excludedPaths\\": [{\\"path\\": \\"/headquarters/employees/?\\"}]}"'
        location = "WestUS"

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'db_name': db_name,
            'gp_name': gp_name,
            'part': partition_key,
            'ttl': default_ttl,
            'nttl': new_default_ttl,
            'conflict_resolution': conflict_resolution_policy,
            'indexing': indexing,
            'loc': location
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg} --capabilities EnableGremlin --backup-policy-type Continuous --locations regionName={loc}')
        self.cmd('az cosmosdb gremlin database create -g {rg} -a {acc} -n {db_name}')

        assert not self.cmd('az cosmosdb gremlin graph exists -g {rg} -a {acc} -d {db_name} -n {gp_name}').get_output_in_json()

        self.cmd('az cosmosdb gremlin graph create -g {rg} -a {acc} -d {db_name} -n {gp_name} -p {part} --ttl {ttl} \
            --conflict-resolution-policy {conflict_resolution} --idx {indexing}', checks=[
            self.check('name', gp_name),
            self.check('resource.partitionKey.paths[0]', partition_key),
            self.check('resource.defaultTtl', default_ttl),
            self.check('resource.conflictResolutionPolicy.mode', "lastWriterWins"),
            self.check('resource.indexingPolicy.excludedPaths[0].path', "/headquarters/employees/?")
        ]).get_output_in_json()

        self.cmd('az cosmosdb gremlin graph update -g {rg} -a {acc} -d {db_name} -n {gp_name} --ttl {nttl}', checks=[
            self.check('resource.defaultTtl', new_default_ttl)
        ]).get_output_in_json()

        self.cmd('az cosmosdb gremlin graph show -g {rg} -a {acc} -d {db_name} -n {gp_name}', checks=[
            self.check('name', gp_name)
        ]).get_output_in_json()

        self.cmd('az cosmosdb gremlin graph list -g {rg} -a {acc} -d {db_name}', checks=[
            self.check('length(@)', 1)
        ]).get_output_in_json()

        assert self.cmd('az cosmosdb gremlin graph exists -g {rg} -a {acc} -d {db_name} -n {gp_name}').get_output_in_json()

        self.cmd('az cosmosdb gremlin graph delete -g {rg} -a {acc} -d {db_name} -n {gp_name} --yes')
        self.cmd('az cosmosdb gremlin graph list -g {rg} -a {acc} -d {db_name}', checks=[
            self.check('length(@)', 0)
        ]).get_output_in_json()

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_gremlin_database_graph_restore')
    def test_cosmosdb_gremlin_database_graph_restore(self, resource_group):
        db_name = self.create_random_name(prefix='cli', length=15)
        gp_name = self.create_random_name(prefix='cli', length=15)
        partition_key = "/thePartitionKey"
        default_ttl = 1000
        new_default_ttl = 2000
        conflict_resolution_policy = '"{\\"mode\\": \\"lastWriterWins\\", \\"conflictResolutionPath\\": \\"/path\\"}"'
        indexing = '"{\\"indexingMode\\": \\"consistent\\", \\"automatic\\": true, \\"includedPaths\\": [{\\"path\\": \\"/*\\"}], \\"excludedPaths\\": [{\\"path\\": \\"/headquarters/employees/?\\"}]}"'
        location = "WestUS"

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'db_name': db_name,
            'gp_name': gp_name,
            'part': partition_key,
            'ttl': default_ttl,
            'nttl': new_default_ttl,
            'conflict_resolution': conflict_resolution_policy,
            'indexing': indexing,
            'loc': location
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg} --capabilities EnableGremlin --backup-policy-type Continuous --locations regionName={loc}')
        self.cmd('az cosmosdb gremlin database create -g {rg} -a {acc} -n {db_name}')

        assert not self.cmd('az cosmosdb gremlin graph exists -g {rg} -a {acc} -d {db_name} -n {gp_name}').get_output_in_json()

        self.cmd('az cosmosdb gremlin graph create -g {rg} -a {acc} -d {db_name} -n {gp_name} -p {part} --ttl {ttl} \
            --conflict-resolution-policy {conflict_resolution} --idx {indexing}', checks=[
            self.check('name', gp_name),
            self.check('resource.partitionKey.paths[0]', partition_key),
            self.check('resource.defaultTtl', default_ttl),
            self.check('resource.conflictResolutionPolicy.mode', "lastWriterWins"),
            self.check('resource.indexingPolicy.excludedPaths[0].path', "/headquarters/employees/?")
        ]).get_output_in_json()

        # restore time
        restore_ts_string = datetime.datetime.utcnow().isoformat()
        self.kwargs.update({
            'rts': restore_ts_string
        })

        import time
        time.sleep(500)

        self.cmd('az cosmosdb gremlin graph show -g {rg} -a {acc} -d {db_name} -n {gp_name}', checks=[
            self.check('name', gp_name)
        ]).get_output_in_json()

        self.cmd('az cosmosdb gremlin graph list -g {rg} -a {acc} -d {db_name}', checks=[
            self.check('length(@)', 1)
        ]).get_output_in_json()

        assert self.cmd('az cosmosdb gremlin graph exists -g {rg} -a {acc} -d {db_name} -n {gp_name}').get_output_in_json()

        # delete graph
        self.cmd('az cosmosdb gremlin graph delete -g {rg} -a {acc} -d {db_name} -n {gp_name} --yes')

        time.sleep(500)

        # restore graph
        self.cmd('az cosmosdb gremlin graph restore -g {rg} -a {acc} -d {db_name} -n {gp_name} --restore-timestamp {rts}')

        time.sleep(500)

        self.cmd('az cosmosdb gremlin graph show -g {rg} -a {acc} -d {db_name} -n {gp_name}', checks=[
            self.check('name', gp_name)
        ]).get_output_in_json()

        self.cmd('az cosmosdb gremlin graph list -g {rg} -a {acc} -d {db_name}', checks=[
            self.check('length(@)', 1)
        ]).get_output_in_json()

        # delete database
        self.cmd('az cosmosdb gremlin database delete -g {rg} -a {acc} -n {db_name} --yes')

        self.cmd('az cosmosdb gremlin database list -g {rg} -a {acc}', checks=[
            self.check('length(@)', 0)
        ]).get_output_in_json()

        time.sleep(500)

        self.cmd('az cosmosdb gremlin database restore -g {rg} -a {acc} -n {db_name} --restore-timestamp {rts}')

        time.sleep(500)

        self.cmd('az cosmosdb gremlin database list -g {rg} -a {acc}', checks=[
            self.check('length(@)', 1)
        ]).get_output_in_json()

        self.cmd('az cosmosdb gremlin graph delete -g {rg} -a {acc} -d {db_name} -n {gp_name} --yes')

        self.cmd('az cosmosdb gremlin graph list -g {rg} -a {acc} -d {db_name}', checks=[
            self.check('length(@)', 0)
        ]).get_output_in_json()

        self.cmd('az cosmosdb gremlin database delete -g {rg} -a {acc} -n {db_name} --yes')

        self.cmd('az cosmosdb gremlin database list -g {rg} -a {acc}', checks=[
            self.check('length(@)', 0)
        ]).get_output_in_json()

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_table_restore')
    def test_cosmosdb_table(self, resource_group):
        table_name = self.create_random_name(prefix='cli', length=15)

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'table_name': table_name,
            'loc': 'eastus2'
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg} --backup-policy-type Continuous --locations regionName={loc} --capabilities EnableTable')

        assert not self.cmd('az cosmosdb table exists -g {rg} -a {acc} -n {table_name}').get_output_in_json()

        self.cmd('az cosmosdb table create -g {rg} -a {acc} -n {table_name}', checks=[
            self.check('name', table_name)
        ]).get_output_in_json()

        self.cmd('az cosmosdb table show -g {rg} -a {acc} -n {table_name}', checks=[
            self.check('name', table_name)
        ]).get_output_in_json()

        self.cmd('az cosmosdb table list -g {rg} -a {acc}', checks=[
            self.check('length(@)', 1)
        ]).get_output_in_json()

        assert self.cmd('az cosmosdb table exists -g {rg} -a {acc} -n {table_name}').get_output_in_json()

        restore_ts_string = datetime.datetime.utcnow().isoformat()

        self.kwargs.update({
            'rts': restore_ts_string
        })
        import time
        time.sleep(500)

        self.cmd('az cosmosdb table delete -g {rg} -a {acc} -n {table_name} --yes')

        self.cmd('az cosmosdb table list -g {rg} -a {acc}', checks=[
            self.check('length(@)', 0)
        ]).get_output_in_json()

        self.cmd('az cosmosdb table restore -g {rg} -a {acc} -n {table_name} --restore-timestamp {rts}').get_output_in_json()

        time.sleep(500)

        self.cmd('az cosmosdb table show -g {rg} -a {acc} -n {table_name}', checks=[
            self.check('name', table_name)
        ]).get_output_in_json()

        self.cmd('az cosmosdb table list -g {rg} -a {acc}', checks=[
            self.check('length(@)', 1)
        ]).get_output_in_json()

        assert self.cmd('az cosmosdb table exists -g {rg} -a {acc} -n {table_name}').get_output_in_json()

        self.cmd('az cosmosdb table delete -g {rg} -a {acc} -n {table_name} --yes')
        self.cmd('az cosmosdb table list -g {rg} -a {acc}', checks=[
            self.check('length(@)', 0)
        ]).get_output_in_json()
