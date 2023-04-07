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


class Cosmosdb_previewInAccountRestoreScenarioTest(ScenarioTest):

#sql
    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_sql_database')
    def test_cosmosdb_sql_database(self, resource_group):
        db_name = self.create_random_name(prefix='cli', length=15)
        location = "WestUS"

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'db_name': db_name,
            'loc': location
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg} --backup-policy-type Continuous --locations regionName={loc}')

        database = self.cmd('az cosmosdb sql database create -g {rg} -a {acc} -n {db_name}').get_output_in_json()
        assert database["name"] == db_name

        database_show = self.cmd('az cosmosdb sql database show -g {rg} -a {acc} -n {db_name}').get_output_in_json()
        assert database_show["name"] == db_name

        assert self.cmd('az cosmosdb sql database exists -g {rg} -a {acc} -n {db_name}').get_output_in_json()
        assert not self.cmd('az cosmosdb sql database exists -g {rg} -a {acc} -n invalid').get_output_in_json()

        database_list = self.cmd('az cosmosdb sql database list -g {rg} -a {acc}').get_output_in_json()
        assert len(database_list) == 1

        self.cmd('az cosmosdb sql database delete -g {rg} -a {acc} -n {db_name} --yes')
        assert not self.cmd('az cosmosdb sql database exists -g {rg} -a {acc} -n {db_name}').get_output_in_json()


    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_sql_container')
    def test_cosmosdb_sql_container(self, resource_group):
        col = self.create_random_name(prefix='cli', length=15)
        location = "WestUS"
        partition = "/pk"

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'db_name': self.create_random_name(prefix='cli', length=15),
            'col': col,
            'indexing': "\"{\"indexingMode\": \"consistent\", \"includedPaths\": [{ \"path\": \"/*\", \"indexes\": [{ \"dataType\": \"String\", \"kind\": \"Range\" }] }], \"excludedPaths\": [{ \"path\": \"/headquarters/employees/?\" } ]}\"",
            'loc': location,
            'part': partition
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg} --backup-policy-type Continuous --locations regionName={loc}')

        self.cmd('az cosmosdb sql database create -g {rg} -a {acc} -n {db_name}')

        collection = self.cmd('az cosmosdb sql container create -g {rg} -a {acc} -d {db_name} -n {col} -p {part}').get_output_in_json()
        assert collection["name"] == col

        collection_show = self.cmd('az cosmosdb sql container show -g {rg} -a {acc} -d {db_name} -n {col}').get_output_in_json()
        assert collection_show["name"] == col

        assert self.cmd('az cosmosdb sql container exists -g {rg} -a {acc} -d {db_name} -n {col}').get_output_in_json()
        assert not self.cmd('az cosmosdb sql container exists -g {rg} -a {acc} -d {db_name} -n invalid').get_output_in_json()

        collection_list = self.cmd('az cosmosdb sql container list -g {rg} -a {acc} -d {db_name}').get_output_in_json()
        assert len(collection_list) == 1

        self.cmd('az cosmosdb sql container delete -g {rg} -a {acc} -d {db_name} -n {col} --yes')


    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_sql_normal_database_restore')
    def test_cosmosdb_sql_normal_database_restore(self, resource_group):
        db_name = self.create_random_name(prefix='cli', length=15)
        location = "WestUS"
        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'db_name': db_name,
            'loc': location
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg} --backup-policy-type Continuous --locations regionName={loc}')

        assert not self.cmd('az cosmosdb sql database exists -g {rg} -a {acc} -n {db_name}').get_output_in_json()

        database_create = self.cmd('az cosmosdb sql database create -g {rg} -a {acc} -n {db_name}').get_output_in_json()
        assert database_create["name"] == db_name

        database_show = self.cmd('az cosmosdb sql database show -g {rg} -a {acc} -n {db_name}').get_output_in_json()
        assert database_show["name"] == db_name

        database_list = self.cmd('az cosmosdb sql database list -g {rg} -a {acc}').get_output_in_json()
        assert len(database_list) == 1

        restore_ts_string = datetime.datetime.utcnow().isoformat()

        self.kwargs.update({
            'rts': restore_ts_string
        })

        assert self.cmd('az cosmosdb sql database exists -g {rg} -a {acc} -n {db_name}').get_output_in_json()

        self.cmd('az cosmosdb sql database delete -g {rg} -a {acc} -n {db_name} --yes')
        database_list = self.cmd('az cosmosdb sql database list -g {rg} -a {acc}').get_output_in_json()
        assert len(database_list) == 0

        self.cmd('az cosmosdb sql database restore -g {rg} -a {acc} -n {db_name} --restore-timestamp {rts}')

        database_restore = self.cmd('az cosmosdb sql database show -g {rg} -a {acc} -n {db_name}').get_output_in_json()
        assert database_restore["name"] == db_name

        database_list = self.cmd('az cosmosdb sql database list -g {rg} -a {acc}').get_output_in_json()
        assert len(database_list) == 1

        container_list = self.cmd('az cosmosdb sql container list -g {rg} -a {acc} -d {db_name}').get_output_in_json()
        assert len(container_list) == 0


    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_sql_shared_database_restore')
    def test_cosmosdb_sql_shared_database_restore(self, resource_group):
        db_name = self.create_random_name(prefix='cli', length=15)
        ctn_name = self.create_random_name(prefix='cli', length=15)
        partition_key = "/thePartitionKey"
        unique_key_policy = '"{\\"uniqueKeys\\": [{\\"paths\\": [\\"/path/to/key1\\"]}, {\\"paths\\": [\\"/path/to/key2\\"]}]}"'
        conflict_resolution_policy = '"{\\"mode\\": \\"lastWriterWins\\", \\"conflictResolutionPath\\": \\"/path\\"}"'
        indexing = '"{\\"indexingMode\\": \\"consistent\\", \\"automatic\\": true, \\"includedPaths\\": [{\\"path\\": \\"/*\\"}], \\"excludedPaths\\": [{\\"path\\": \\"/headquarters/employees/?\\"}]}"'
        location = "WestUS"
        tp1 = 1000

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'db_name': db_name,
            'ctn_name': ctn_name,
            'part': partition_key,
            'unique_key': unique_key_policy,
            "conflict_resolution": conflict_resolution_policy,
            "indexing": indexing,
            'loc': location,
            'tp1': tp1
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg} --backup-policy-type Continuous --locations regionName={loc}')
        self.cmd('az cosmosdb sql database create -g {rg} -a {acc} -n {db_name} --throughput {tp1}')

        assert not self.cmd('az cosmosdb sql container exists -g {rg} -a {acc} -d {db_name} -n {ctn_name}').get_output_in_json()

        container_create = self.cmd('az cosmosdb sql container create -g {rg} -a {acc} -d {db_name} -n {ctn_name} -p {part} --unique-key-policy {unique_key} --conflict-resolution-policy {conflict_resolution} --idx {indexing}').get_output_in_json()

        assert container_create["name"] == ctn_name
        assert container_create["resource"]["partitionKey"]["paths"][0] == partition_key
        assert len(container_create["resource"]["uniqueKeyPolicy"]["uniqueKeys"]) == 2
        assert container_create["resource"]["conflictResolutionPolicy"]["mode"] == "lastWriterWins"
        assert container_create["resource"]["indexingPolicy"]["excludedPaths"][0]["path"] == "/headquarters/employees/?"

        container_show = self.cmd('az cosmosdb sql container show -g {rg} -a {acc} -d {db_name} -n {ctn_name}').get_output_in_json()
        assert container_show["name"] == ctn_name

        container_list = self.cmd('az cosmosdb sql container list -g {rg} -a {acc} -d {db_name}').get_output_in_json()
        assert len(container_list) == 1

        restore_ts_string = datetime.datetime.utcnow().isoformat()

        self.kwargs.update({
            'rts': restore_ts_string
        })
        import time
        time.sleep(300)

        assert self.cmd('az cosmosdb sql container exists -g {rg} -a {acc} -d {db_name} -n {ctn_name}').get_output_in_json()

        self.cmd('az cosmosdb sql container delete -g {rg} -a {acc} -d {db_name} -n {ctn_name} --yes')
        container_list = self.cmd('az cosmosdb sql container list -g {rg} -a {acc} -d {db_name}').get_output_in_json()
        assert len(container_list) == 0

        self.assertRaises(Exception, lambda: self.cmd('az cosmosdb sql container restore -g {rg} -a {acc} -d {db_name} -n {ctn_name} --restore-timestamp {rts}'))
        #self.cmd('az cosmosdb sql container restore -g {rg} -a {acc} -d {db_name} -n {ctn_name} --restore-timestamp {rts}')

        container_list = self.cmd('az cosmosdb sql container list -g {rg} -a {acc} -d {db_name}').get_output_in_json()
        assert len(container_list) == 0

        self.cmd('az cosmosdb sql database delete -g {rg} -a {acc} -n {db_name} --yes')
        database_list = self.cmd('az cosmosdb sql database list -g {rg} -a {acc}').get_output_in_json()
        assert len(database_list) == 0

        import time
        time.sleep(500)

        self.cmd('az cosmosdb sql database restore -g {rg} -a {acc} -n {db_name} --restore-timestamp {rts}')

        database_restore = self.cmd('az cosmosdb sql database show -g {rg} -a {acc} -n {db_name}').get_output_in_json()
        assert database_restore["name"] == db_name

        container_list = self.cmd('az cosmosdb sql container list -g {rg} -a {acc} -d {db_name}').get_output_in_json()
        assert len(container_list) == 1

        container_show = self.cmd('az cosmosdb sql container show -g {rg} -a {acc} -d {db_name} -n {ctn_name}').get_output_in_json()
        assert container_show["name"] == ctn_name

        self.cmd('az cosmosdb sql database delete -g {rg} -a {acc} -n {db_name} --yes')
        database_list = self.cmd('az cosmosdb sql database list -g {rg} -a {acc}').get_output_in_json()
        assert len(database_list) == 0


    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_sql_normal_database_prov_container_restore')
    def test_cosmosdb_sql_normal_database_prov_container_restore(self, resource_group):
        db_name = self.create_random_name(prefix='cli', length=15)
        ctn_name = self.create_random_name(prefix='cli', length=15)
        partition_key = "/thePartitionKey"
        unique_key_policy = '"{\\"uniqueKeys\\": [{\\"paths\\": [\\"/path/to/key1\\"]}, {\\"paths\\": [\\"/path/to/key2\\"]}]}"'
        conflict_resolution_policy = '"{\\"mode\\": \\"lastWriterWins\\", \\"conflictResolutionPath\\": \\"/path\\"}"'
        indexing = '"{\\"indexingMode\\": \\"consistent\\", \\"automatic\\": true, \\"includedPaths\\": [{\\"path\\": \\"/*\\"}], \\"excludedPaths\\": [{\\"path\\": \\"/headquarters/employees/?\\"}]}"'
        location = "WestUS"

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'db_name': db_name,
            'ctn_name': ctn_name,
            'part': partition_key,
            'unique_key': unique_key_policy,
            "conflict_resolution": conflict_resolution_policy,
            "indexing": indexing,
            'loc': location
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg} --backup-policy-type Continuous --locations regionName={loc}')
        self.cmd('az cosmosdb sql database create -g {rg} -a {acc} -n {db_name}')

        assert not self.cmd('az cosmosdb sql container exists -g {rg} -a {acc} -d {db_name} -n {ctn_name}').get_output_in_json()

        container_create = self.cmd('az cosmosdb sql container create -g {rg} -a {acc} -d {db_name} -n {ctn_name} -p {part} --unique-key-policy {unique_key} --conflict-resolution-policy {conflict_resolution} --idx {indexing}').get_output_in_json()

        assert container_create["name"] == ctn_name
        assert container_create["resource"]["partitionKey"]["paths"][0] == partition_key
        assert len(container_create["resource"]["uniqueKeyPolicy"]["uniqueKeys"]) == 2
        assert container_create["resource"]["conflictResolutionPolicy"]["mode"] == "lastWriterWins"
        assert container_create["resource"]["indexingPolicy"]["excludedPaths"][0]["path"] == "/headquarters/employees/?"

        container_update = self.cmd('az cosmosdb sql container update -g {rg} -a {acc} -d {db_name} -n {ctn_name}').get_output_in_json()

        container_show = self.cmd('az cosmosdb sql container show -g {rg} -a {acc} -d {db_name} -n {ctn_name}').get_output_in_json()
        assert container_show["name"] == ctn_name

        container_list = self.cmd('az cosmosdb sql container list -g {rg} -a {acc} -d {db_name}').get_output_in_json()
        assert len(container_list) == 1

        restore_ts_string = datetime.datetime.utcnow().isoformat()

        self.kwargs.update({
            'rts': restore_ts_string
        })
        import time
        time.sleep(300)

        assert self.cmd('az cosmosdb sql container exists -g {rg} -a {acc} -d {db_name} -n {ctn_name}').get_output_in_json()

        self.cmd('az cosmosdb sql container delete -g {rg} -a {acc} -d {db_name} -n {ctn_name} --yes')
        container_list = self.cmd('az cosmosdb sql container list -g {rg} -a {acc} -d {db_name}').get_output_in_json()
        assert len(container_list) == 0

        #self.assertRaises(Exception, lambda: self.cmd('az cosmosdb sql container restore -g {rg} -a {acc} -d {db_name} -n {ctn_name} --restore-timestamp {rts}'))
        self.cmd('az cosmosdb sql container restore -g {rg} -a {acc} -d {db_name} -n {ctn_name} --restore-timestamp {rts}')

        container_list = self.cmd('az cosmosdb sql container list -g {rg} -a {acc} -d {db_name}').get_output_in_json()
        assert len(container_list) == 1

        self.cmd('az cosmosdb sql database delete -g {rg} -a {acc} -n {db_name} --yes')
        database_list = self.cmd('az cosmosdb sql database list -g {rg} -a {acc}').get_output_in_json()
        assert len(database_list) == 0

        self.cmd('az cosmosdb sql database restore -g {rg} -a {acc} -n {db_name} --restore-timestamp {rts}')

        database_restore = self.cmd('az cosmosdb sql database show -g {rg} -a {acc} -n {db_name}').get_output_in_json()
        assert database_restore["name"] == db_name

        container_list = self.cmd('az cosmosdb sql container list -g {rg} -a {acc} -d {db_name}').get_output_in_json()
        assert len(container_list) == 0

        self.cmd('az cosmosdb sql container restore -g {rg} -a {acc} -d {db_name} -n {ctn_name} --restore-timestamp {rts}')

        container_list = self.cmd('az cosmosdb sql container list -g {rg} -a {acc} -d {db_name}').get_output_in_json()
        assert len(container_list) == 1

        container_show = self.cmd('az cosmosdb sql container show -g {rg} -a {acc} -d {db_name} -n {ctn_name}').get_output_in_json()
        assert container_show["name"] == ctn_name


    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_sql_shared_database_prov_container_restore')
    def test_cosmosdb_sql_shared_database_prov_container_restore(self, resource_group):
        db_name = self.create_random_name(prefix='cli', length=15)
        ctn_name = self.create_random_name(prefix='cli', length=15)
        partition_key = "/thePartitionKey"
        unique_key_policy = '"{\\"uniqueKeys\\": [{\\"paths\\": [\\"/path/to/key1\\"]}, {\\"paths\\": [\\"/path/to/key2\\"]}]}"'
        conflict_resolution_policy = '"{\\"mode\\": \\"lastWriterWins\\", \\"conflictResolutionPath\\": \\"/path\\"}"'
        indexing = '"{\\"indexingMode\\": \\"consistent\\", \\"automatic\\": true, \\"includedPaths\\": [{\\"path\\": \\"/*\\"}], \\"excludedPaths\\": [{\\"path\\": \\"/headquarters/employees/?\\"}]}"'
        location = "WestUS"
        tp1 = 1000

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'db_name': db_name,
            'ctn_name': ctn_name,
            'part': partition_key,
            'unique_key': unique_key_policy,
            "conflict_resolution": conflict_resolution_policy,
            "indexing": indexing,
            'loc': location,
            'tp1': tp1
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg} --backup-policy-type Continuous --locations regionName={loc}')
        self.cmd('az cosmosdb sql database create -g {rg} -a {acc} -n {db_name} --throughput {tp1}')

        assert not self.cmd('az cosmosdb sql container exists -g {rg} -a {acc} -d {db_name} -n {ctn_name}').get_output_in_json()

        container_create = self.cmd('az cosmosdb sql container create -g {rg} -a {acc} -d {db_name} -n {ctn_name} -p {part} --unique-key-policy {unique_key} --conflict-resolution-policy {conflict_resolution} --idx {indexing} --throughput {tp1}').get_output_in_json()

        assert container_create["name"] == ctn_name
        assert container_create["resource"]["partitionKey"]["paths"][0] == partition_key
        assert len(container_create["resource"]["uniqueKeyPolicy"]["uniqueKeys"]) == 2
        assert container_create["resource"]["conflictResolutionPolicy"]["mode"] == "lastWriterWins"
        assert container_create["resource"]["indexingPolicy"]["excludedPaths"][0]["path"] == "/headquarters/employees/?"

        container_update = self.cmd('az cosmosdb sql container update -g {rg} -a {acc} -d {db_name} -n {ctn_name}').get_output_in_json()

        container_show = self.cmd('az cosmosdb sql container show -g {rg} -a {acc} -d {db_name} -n {ctn_name}').get_output_in_json()
        assert container_show["name"] == ctn_name

        container_list = self.cmd('az cosmosdb sql container list -g {rg} -a {acc} -d {db_name}').get_output_in_json()
        assert len(container_list) == 1

        restore_ts_string = datetime.datetime.utcnow().isoformat()

        self.kwargs.update({
            'rts': restore_ts_string
        })
        import time
        time.sleep(300)

        assert self.cmd('az cosmosdb sql container exists -g {rg} -a {acc} -d {db_name} -n {ctn_name}').get_output_in_json()

        self.cmd('az cosmosdb sql container delete -g {rg} -a {acc} -d {db_name} -n {ctn_name} --yes')
        container_list = self.cmd('az cosmosdb sql container list -g {rg} -a {acc} -d {db_name}').get_output_in_json()
        assert len(container_list) == 0

        #self.assertRaises(Exception, lambda: self.cmd('az cosmosdb sql container restore -g {rg} -a {acc} -d {db_name} -n {ctn_name} --restore-timestamp {rts}'))
        self.cmd('az cosmosdb sql container restore -g {rg} -a {acc} -d {db_name} -n {ctn_name} --restore-timestamp {rts}')

        container_list = self.cmd('az cosmosdb sql container list -g {rg} -a {acc} -d {db_name}').get_output_in_json()
        assert len(container_list) == 1

        self.cmd('az cosmosdb sql database delete -g {rg} -a {acc} -n {db_name} --yes')
        database_list = self.cmd('az cosmosdb sql database list -g {rg} -a {acc}').get_output_in_json()
        assert len(database_list) == 0

        self.cmd('az cosmosdb sql database restore -g {rg} -a {acc} -n {db_name} --restore-timestamp {rts}')

        database_restore = self.cmd('az cosmosdb sql database show -g {rg} -a {acc} -n {db_name}').get_output_in_json()
        assert database_restore["name"] == db_name

        container_list = self.cmd('az cosmosdb sql container list -g {rg} -a {acc} -d {db_name}').get_output_in_json()
        assert len(container_list) == 0

        self.cmd('az cosmosdb sql container restore -g {rg} -a {acc} -d {db_name} -n {ctn_name} --restore-timestamp {rts}')

        container_list = self.cmd('az cosmosdb sql container list -g {rg} -a {acc} -d {db_name}').get_output_in_json()
        assert len(container_list) == 1

        container_show = self.cmd('az cosmosdb sql container show -g {rg} -a {acc} -d {db_name} -n {ctn_name}').get_output_in_json()
        assert container_show["name"] == ctn_name


#mongo
    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_mongodb_database')
    def test_cosmosdb_mongodb_database(self, resource_group):
        db_name = self.create_random_name(prefix='cli', length=15)
        location = "WestUS"

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'db_name': db_name,
            'loc': location
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg} --kind MongoDB --server-version 3.6 --backup-policy-type Continuous --locations regionName={loc}')

        assert not self.cmd('az cosmosdb mongodb database exists -g {rg} -a {acc} -n {db_name}').get_output_in_json()

        database_create = self.cmd('az cosmosdb mongodb database create -g {rg} -a {acc} -n {db_name}').get_output_in_json()
        assert database_create["name"] == db_name

        database_show = self.cmd('az cosmosdb mongodb database show -g {rg} -a {acc} -n {db_name}').get_output_in_json()
        assert database_show["name"] == db_name

        database_list = self.cmd('az cosmosdb mongodb database list -g {rg} -a {acc}').get_output_in_json()
        assert len(database_list) == 1

        assert self.cmd('az cosmosdb mongodb database exists -g {rg} -a {acc} -n {db_name}').get_output_in_json()

        self.cmd('az cosmosdb mongodb database delete -g {rg} -a {acc} -n {db_name} --yes')
        database_list = self.cmd('az cosmosdb mongodb database list -g {rg} -a {acc}').get_output_in_json()
        assert len(database_list) == 0


    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_mongodb_collection')
    def test_cosmosdb_mongodb_collection(self, resource_group):
        col = self.create_random_name(prefix='cli', length=15)
        partition_key = "/thePartitionKey"
        location = "WestUS"

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'db_name': self.create_random_name(prefix='cli', length=15),
            'col': col,
            'indexing': "\"{\"indexingMode\": \"consistent\", \"includedPaths\": [{ \"path\": \"/*\", \"indexes\": [{ \"dataType\": \"String\", \"kind\": \"Range\" }] }], \"excludedPaths\": [{ \"path\": \"/headquarters/employees/?\" } ]}\"",
            'part': partition_key,
            'loc': location
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg} --kind MongoDB --server-version 3.6 --backup-policy-type Continuous --locations regionName={loc}')

        self.cmd('az cosmosdb mongodb database create -g {rg} -a {acc} -n {db_name}')

        collection = self.cmd('az cosmosdb mongodb collection create -g {rg} -a {acc} -d {db_name} -n {col}').get_output_in_json()
        assert collection["name"] == col

        collection_show = self.cmd('az cosmosdb mongodb collection show -g {rg} -a {acc} -d {db_name} -n {col}').get_output_in_json()
        assert collection_show["name"] == col

        assert self.cmd('az cosmosdb mongodb collection exists -g {rg} -a {acc} -d {db_name} -n {col}').get_output_in_json()
        assert not self.cmd('az cosmosdb mongodb collection exists -g {rg} -a {acc} -d {db_name} -n invalid').get_output_in_json()

        collection_list = self.cmd('az cosmosdb mongodb collection list -g {rg} -a {acc} -d {db_name}').get_output_in_json()
        assert len(collection_list) == 1

        self.cmd('az cosmosdb mongodb collection delete -g {rg} -a {acc} -d {db_name} -n {col} --yes')


    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_mongodb_normal_database_prov_collection_restore')
    def test_cosmosdb_mongodb_normal_database_prov_collection_restore(self, resource_group):
        col_name = self.create_random_name(prefix='cli', length=15)
        location = "WestUS"

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'db_name': self.create_random_name(prefix='cli', length=15),
            'col_name': col_name,
            'shard_key': "theShardKey",
            'indexes': '"[{\\"key\\": {\\"keys\\": [\\"_ts\\"]},\\"options\\": {\\"expireAfterSeconds\\": 1000}}]"',
            'loc': location
        })

        # Create normal database + prov collection
        self.cmd('az cosmosdb create -n {acc} -g {rg} --kind MongoDB --server-version 3.6 --backup-policy-type Continuous --locations regionName={loc}')
        self.cmd('az cosmosdb mongodb database create -g {rg} -a {acc} -n {db_name}')

        assert not self.cmd('az cosmosdb mongodb collection exists -g {rg} -a {acc} -d {db_name} -n {col_name}').get_output_in_json()

        collection_create = self.cmd(
            'az cosmosdb mongodb collection create -g {rg} -a {acc} -d {db_name} -n {col_name} --shard {shard_key}').get_output_in_json()
        assert collection_create["name"] == col_name

        indexes_size = len(collection_create["resource"]["indexes"])
        # collection_update = self.cmd(
        #    'az cosmosdb mongodb collection update -g {rg} -a {acc} -d {db_name} -n {col_name} --idx {indexes}').get_output_in_json()
        # assert len(collection_update["resource"]["indexes"]) == indexes_size + 1

        collection_show = self.cmd(
            'az cosmosdb mongodb collection show -g {rg} -a {acc} -d {db_name} -n {col_name}').get_output_in_json()
        assert collection_show["name"] == col_name

        collection_list = self.cmd(
            'az cosmosdb mongodb collection list -g {rg} -a {acc} -d {db_name}').get_output_in_json()
        assert len(collection_list) == 1

        assert self.cmd('az cosmosdb mongodb collection exists -g {rg} -a {acc} -d {db_name} -n {col_name}').get_output_in_json()

        restore_ts_string = datetime.datetime.utcnow().isoformat()

        self.kwargs.update({
            'rts': restore_ts_string
        })
        import time
        time.sleep(300)

        # Restore collection and validate collection got restored
        self.cmd('az cosmosdb mongodb collection delete -g {rg} -a {acc} -d {db_name} -n {col_name} --yes')
        collection_list = self.cmd(
            'az cosmosdb mongodb collection list -g {rg} -a {acc} -d {db_name}').get_output_in_json()
        assert len(collection_list) == 0

        self.cmd('az cosmosdb mongodb collection restore -g {rg} -a {acc} -d {db_name} -n {col_name} --restore-timestamp {rts}').get_output_in_json()

        collection_list = self.cmd(
            'az cosmosdb mongodb collection list -g {rg} -a {acc} -d {db_name}').get_output_in_json()
        assert len(collection_list) == 1

        # Restore database and validate database got restored but not collections
        self.cmd('az cosmosdb mongodb database delete -g {rg} -a {acc} -n {db_name} --yes')
        database_list = self.cmd('az cosmosdb mongodb database list -g {rg} -a {acc}').get_output_in_json()
        assert len(database_list) == 0

        self.cmd('az cosmosdb mongodb database restore -g {rg} -a {acc} -n {db_name} --restore-timestamp {rts}').get_output_in_json()

        database_list = self.cmd('az cosmosdb mongodb database list -g {rg} -a {acc}').get_output_in_json()
        assert len(database_list) == 1

        collection_list = self.cmd(
            'az cosmosdb mongodb collection list -g {rg} -a {acc} -d {db_name}').get_output_in_json()
        assert len(collection_list) == 0

        # Restore collection and validate collection got restored
        self.cmd('az cosmosdb mongodb collection restore -g {rg} -a {acc} -d {db_name} -n {col_name} --restore-timestamp {rts}').get_output_in_json()

        collection_list = self.cmd(
            'az cosmosdb mongodb collection list -g {rg} -a {acc} -d {db_name}').get_output_in_json()
        assert len(collection_list) == 1

        # cleanup
        self.cmd('az cosmosdb mongodb database delete -g {rg} -a {acc} -n {db_name} --yes')
        database_list = self.cmd('az cosmosdb mongodb database list -g {rg} -a {acc}').get_output_in_json()
        assert len(database_list) == 0
        collection_list = self.cmd(
            'az cosmosdb mongodb collection list -g {rg} -a {acc} -d {db_name}').get_output_in_json()
        assert len(collection_list) == 0


    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_mongodb_shared_database_prov_collection_restore')
    def test_cosmosdb_mongodb_shared_database_prov_collection_restore(self, resource_group):
        col_name = self.create_random_name(prefix='cli', length=15)
        col_name2 = self.create_random_name(prefix='cli', length=15)
        location = "WestUS"
        tp1 = 1000
        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'db_name': self.create_random_name(prefix='cli', length=15),
            'col_name': col_name,
            'col_name2': col_name2,
            'shard_key': "theShardKey",
            'indexes': '"[{\\"key\\": {\\"keys\\": [\\"_ts\\"]},\\"options\\": {\\"expireAfterSeconds\\": 1000}}]"',
            'loc': location,
            'tp1': tp1
        })

        # create mongodb shared database + shared collection + prov collection
        self.cmd('az cosmosdb create -n {acc} -g {rg} --kind MongoDB --server-version 3.6 --backup-policy-type Continuous --locations regionName={loc}')
        self.cmd('az cosmosdb mongodb database create -g {rg} -a {acc} -n {db_name} --throughput {tp1}')

        assert not self.cmd('az cosmosdb mongodb collection exists -g {rg} -a {acc} -d {db_name} -n {col_name}').get_output_in_json()

        collection_create = self.cmd(
            'az cosmosdb mongodb collection create -g {rg} -a {acc} -d {db_name} -n {col_name} --shard {shard_key}').get_output_in_json()
        assert collection_create["name"] == col_name

        collection_create = self.cmd(
            'az cosmosdb mongodb collection create -g {rg} -a {acc} -d {db_name} -n {col_name2} --shard {shard_key} --throughput {tp1}').get_output_in_json()
        assert collection_create["name"] == col_name2

        indexes_size = len(collection_create["resource"]["indexes"])
        # collection_update = self.cmd(
        #     'az cosmosdb mongodb collection update -g {rg} -a {acc} -d {db_name} -n {col_name} --idx {indexes}').get_output_in_json()
        # assert len(collection_update["resource"]["indexes"]) == indexes_size + 1

        collection_show = self.cmd(
            'az cosmosdb mongodb collection show -g {rg} -a {acc} -d {db_name} -n {col_name}').get_output_in_json()
        assert collection_show["name"] == col_name

        collection_list = self.cmd(
            'az cosmosdb mongodb collection list -g {rg} -a {acc} -d {db_name}').get_output_in_json()
        assert len(collection_list) == 2

        assert self.cmd('az cosmosdb mongodb collection exists -g {rg} -a {acc} -d {db_name} -n {col_name}').get_output_in_json()

        restore_ts_string = datetime.datetime.utcnow().isoformat()

        self.kwargs.update({
            'rts': restore_ts_string
        })
        import time
        time.sleep(300)

        self.cmd('az cosmosdb mongodb collection delete -g {rg} -a {acc} -d {db_name} -n {col_name} --yes')
        self.cmd('az cosmosdb mongodb collection delete -g {rg} -a {acc} -d {db_name} -n {col_name2} --yes')

        collection_list = self.cmd(
            'az cosmosdb mongodb collection list -g {rg} -a {acc} -d {db_name}').get_output_in_json()
        assert len(collection_list) == 0

        self.assertRaises(Exception, lambda: self.cmd('az cosmosdb mongodb collection restore -g {rg} -a {acc} -d {db_name} -n {col_name} --restore-timestamp {rts}').get_output_in_json())

        collection_list = self.cmd(
            'az cosmosdb mongodb collection list -g {rg} -a {acc} -d {db_name}').get_output_in_json()
        assert len(collection_list) == 0

        self.cmd('az cosmosdb mongodb database delete -g {rg} -a {acc} -n {db_name} --yes')
        database_list = self.cmd('az cosmosdb mongodb database list -g {rg} -a {acc}').get_output_in_json()
        assert len(database_list) == 0

        # delete and restore shared database. that should restore only shared collection with it
        self.cmd('az cosmosdb mongodb database restore -g {rg} -a {acc} -n {db_name} --restore-timestamp {rts}').get_output_in_json()

        database_list = self.cmd('az cosmosdb mongodb database list -g {rg} -a {acc}').get_output_in_json()
        assert len(database_list) == 1

        collection_list = self.cmd(
            'az cosmosdb mongodb collection list -g {rg} -a {acc} -d {db_name}').get_output_in_json()
        assert len(collection_list) == 1

        # Restore collection and validate collection got restored
        self.cmd('az cosmosdb mongodb collection restore -g {rg} -a {acc} -d {db_name} -n {col_name2} --restore-timestamp {rts}').get_output_in_json()

        collection_list = self.cmd(
            'az cosmosdb mongodb collection list -g {rg} -a {acc} -d {db_name}').get_output_in_json()
        assert len(collection_list) == 2

        # cleanup
        self.cmd('az cosmosdb mongodb database delete -g {rg} -a {acc} -n {db_name} --yes')
        database_list = self.cmd('az cosmosdb mongodb database list -g {rg} -a {acc}').get_output_in_json()
        assert len(database_list) == 0
