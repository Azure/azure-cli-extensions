# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from knack.util import CLIError
from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from datetime import datetime, timedelta, timezone
from dateutil import parser
import datetime

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class Cosmosdb_previewInAccountRestoreScenarioTest(ScenarioTest):

#sql
    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_database')
    def test_cosmosdb_database(self, resource_group):

        db_name = self.create_random_name(prefix='cli', length=15)

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'db_name': db_name,
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg}')

        database = self.cmd('az cosmosdb database create -g {rg} -n {acc} -d {db_name}').get_output_in_json()
        assert database["id"] == db_name

        database_show = self.cmd('az cosmosdb database show -g {rg} -n {acc} -d {db_name}').get_output_in_json()
        assert database_show["id"] == db_name

        assert self.cmd('az cosmosdb database exists -g {rg} -n {acc} -d {db_name}').get_output_in_json()
        assert not self.cmd('az cosmosdb database exists -g {rg} -n {acc} -d invalid').get_output_in_json()

        database_list = self.cmd('az cosmosdb database list -g {rg} -n {acc}').get_output_in_json()
        assert len(database_list) == 1

        self.cmd('az cosmosdb database delete -g {rg} -n {acc} -d {db_name} --yes')
        assert not self.cmd('az cosmosdb database exists -g {rg} -n {acc} -d {db_name}').get_output_in_json()


    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_collection')
    def test_cosmosdb_collection(self, resource_group):

        col = self.create_random_name(prefix='cli', length=15)
        throughput = 500
        default_ttl = 1000

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'db_name': self.create_random_name(prefix='cli', length=15),
            'col': col,
            'throughput': throughput,
            'ttl': default_ttl,
            'indexing': "\"{\"indexingMode\": \"consistent\", \"includedPaths\": [{ \"path\": \"/*\", \"indexes\": [{ \"dataType\": \"String\", \"kind\": \"Range\" }] }], \"excludedPaths\": [{ \"path\": \"/headquarters/employees/?\" } ]}\""
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg}')

        self.cmd('az cosmosdb database create -g {rg} -n {acc} -d {db_name}')

        collection = self.cmd('az cosmosdb collection create -g {rg} -n {acc} -d {db_name} -c {col} --default-ttl 0').get_output_in_json()
        assert collection["collection"]["id"] == col

        collection_show = self.cmd('az cosmosdb collection show -g {rg} -n {acc} -d {db_name} -c {col}').get_output_in_json()
        assert collection_show["collection"]["id"] == col

        assert self.cmd('az cosmosdb collection exists -g {rg} -n {acc} -d {db_name} -c {col}').get_output_in_json()
        assert not self.cmd('az cosmosdb collection exists -g {rg} -n {acc} -d {db_name} -c invalid').get_output_in_json()

        collection_list = self.cmd('az cosmosdb collection list -g {rg} -n {acc} -d {db_name}').get_output_in_json()
        assert len(collection_list) == 1

        # update throughput
        throughput_update = self.cmd('az cosmosdb collection update --throughput {throughput} -g {rg} -n {acc} -d {db_name} -c {col}').get_output_in_json()
        assert throughput_update["offer"]["content"]["offerThroughput"] == throughput

        # update ttl
        ttl_update = self.cmd('az cosmosdb collection update --default-ttl {ttl} -g {rg} -n {acc} -d {db_name} -c {col}').get_output_in_json()
        assert ttl_update["collection"]["defaultTtl"] == default_ttl

        # remove ttl
        disable_ttl = self.cmd('az cosmosdb collection update --default-ttl 0 -g {rg} -n {acc} -d {db_name} -c {col}').get_output_in_json()
        assert "defaultTtl" not in disable_ttl["collection"]

        self.cmd('az cosmosdb collection delete -g {rg} -n {acc} -d {db_name} -c {col} --yes')

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_sql_database')
    def test_cosmosdb_sql_database(self, resource_group):
        db_name = self.create_random_name(prefix='cli', length=15)
        location = "CentralUS"
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



    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_sql_container')
    def test_cosmosdb_sql_container(self, resource_group):
        db_name = self.create_random_name(prefix='cli', length=15)
        ctn_name = self.create_random_name(prefix='cli', length=15)
        partition_key = "/thePartitionKey"
        default_ttl = 1000
        new_default_ttl = 2000
        unique_key_policy = '"{\\"uniqueKeys\\": [{\\"paths\\": [\\"/path/to/key1\\"]}, {\\"paths\\": [\\"/path/to/key2\\"]}]}"'
        conflict_resolution_policy = '"{\\"mode\\": \\"lastWriterWins\\", \\"conflictResolutionPath\\": \\"/path\\"}"'
        indexing = '"{\\"indexingMode\\": \\"consistent\\", \\"automatic\\": true, \\"includedPaths\\": [{\\"path\\": \\"/*\\"}], \\"excludedPaths\\": [{\\"path\\": \\"/headquarters/employees/?\\"}]}"'
        location = "CentralUS"

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'db_name': db_name,
            'ctn_name': ctn_name,
            'part': partition_key,
            'ttl': default_ttl,
            'nttl': new_default_ttl,
            'unique_key': unique_key_policy,
            "conflict_resolution": conflict_resolution_policy,
            "indexing": indexing,
            'loc': location
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg} --backup-policy-type Continuous --locations regionName={loc}')
        self.cmd('az cosmosdb sql database create -g {rg} -a {acc} -n {db_name}')

        assert not self.cmd('az cosmosdb sql container exists -g {rg} -a {acc} -d {db_name} -n {ctn_name}').get_output_in_json()

        container_create = self.cmd('az cosmosdb sql container create -g {rg} -a {acc} -d {db_name} -n {ctn_name} -p {part} --ttl {ttl} --unique-key-policy {unique_key} --conflict-resolution-policy {conflict_resolution} --idx {indexing}').get_output_in_json()

        assert container_create["name"] == ctn_name
        assert container_create["resource"]["partitionKey"]["paths"][0] == partition_key
        assert container_create["resource"]["defaultTtl"] == default_ttl
        assert len(container_create["resource"]["uniqueKeyPolicy"]["uniqueKeys"]) == 2
        assert container_create["resource"]["conflictResolutionPolicy"]["mode"] == "lastWriterWins"
        assert container_create["resource"]["indexingPolicy"]["excludedPaths"][0]["path"] == "/headquarters/employees/?"

        container_update = self.cmd('az cosmosdb sql container update -g {rg} -a {acc} -d {db_name} -n {ctn_name} --ttl {nttl}').get_output_in_json()
        assert container_update["resource"]["defaultTtl"] == new_default_ttl

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
        import time
        time.sleep(300)

        container_list = self.cmd('az cosmosdb sql container list -g {rg} -a {acc} -d {db_name}').get_output_in_json()
        assert len(container_list) == 1

        self.cmd('az cosmosdb sql database delete -g {rg} -a {acc} -n {db_name} --yes')
        database_list = self.cmd('az cosmosdb sql database list -g {rg} -a {acc}').get_output_in_json()
        assert len(database_list) == 0

        import time
        time.sleep(300)

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

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_sql_shared_resources_restore')
    def test_cosmosdb_sql_shared_resources_restore(self, resource_group):
        db_name = self.create_random_name(prefix='cli', length=15)
        ctn_name = self.create_random_name(prefix='cli', length=15)
        partition_key = "/thePartitionKey"
        default_ttl = 1000
        new_default_ttl = 2000
        unique_key_policy = '"{\\"uniqueKeys\\": [{\\"paths\\": [\\"/path/to/key1\\"]}, {\\"paths\\": [\\"/path/to/key2\\"]}]}"'
        conflict_resolution_policy = '"{\\"mode\\": \\"lastWriterWins\\", \\"conflictResolutionPath\\": \\"/path\\"}"'
        indexing = '"{\\"indexingMode\\": \\"consistent\\", \\"automatic\\": true, \\"includedPaths\\": [{\\"path\\": \\"/*\\"}], \\"excludedPaths\\": [{\\"path\\": \\"/headquarters/employees/?\\"}]}"'
        location = "CentralUS"
        tp1 = 1000

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'db_name': db_name,
            'ctn_name': ctn_name,
            'part': partition_key,
            'ttl': default_ttl,
            'nttl': new_default_ttl,
            'unique_key': unique_key_policy,
            "conflict_resolution": conflict_resolution_policy,
            "indexing": indexing,
            'loc': location,
            'tp1': tp1
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg} --backup-policy-type Continuous --locations regionName={loc}')
        self.cmd('az cosmosdb sql database create -g {rg} -a {acc} -n {db_name} --throughput {tp1}')

        assert not self.cmd('az cosmosdb sql container exists -g {rg} -a {acc} -d {db_name} -n {ctn_name}').get_output_in_json()

        container_create = self.cmd('az cosmosdb sql container create -g {rg} -a {acc} -d {db_name} -n {ctn_name} -p {part} --ttl {ttl} --unique-key-policy {unique_key} --conflict-resolution-policy {conflict_resolution} --idx {indexing}').get_output_in_json()

        assert container_create["name"] == ctn_name
        assert container_create["resource"]["partitionKey"]["paths"][0] == partition_key
        assert container_create["resource"]["defaultTtl"] == default_ttl
        assert len(container_create["resource"]["uniqueKeyPolicy"]["uniqueKeys"]) == 2
        assert container_create["resource"]["conflictResolutionPolicy"]["mode"] == "lastWriterWins"
        assert container_create["resource"]["indexingPolicy"]["excludedPaths"][0]["path"] == "/headquarters/employees/?"

        container_update = self.cmd('az cosmosdb sql container update -g {rg} -a {acc} -d {db_name} -n {ctn_name} --ttl {nttl}').get_output_in_json()
        assert container_update["resource"]["defaultTtl"] == new_default_ttl

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

#mongo

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_mongodb_database')
    def test_cosmosdb_mongodb_database(self, resource_group):
        db_name = self.create_random_name(prefix='cli', length=15)

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'db_name': db_name,
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg} --kind MongoDB')

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

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_mongodb_collection')
    def test_cosmosdb_mongodb_collection(self, resource_group):
        col_name = self.create_random_name(prefix='cli', length=15)
        location = "CentralUS"

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'db_name': self.create_random_name(prefix='cli', length=15),
            'col_name': col_name,
            'shard_key': "theShardKey",
            'indexes': '"[{\\"key\\": {\\"keys\\": [\\"_ts\\"]},\\"options\\": {\\"expireAfterSeconds\\": 1000}}]"',
            'loc': location
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg} --kind MongoDB --server-version 3.6 --backup-policy-type Continuous --locations regionName={loc}')
        self.cmd('az cosmosdb mongodb database create -g {rg} -a {acc} -n {db_name}')

        assert not self.cmd('az cosmosdb mongodb collection exists -g {rg} -a {acc} -d {db_name} -n {col_name}').get_output_in_json()

        collection_create = self.cmd(
            'az cosmosdb mongodb collection create -g {rg} -a {acc} -d {db_name} -n {col_name} --shard {shard_key}').get_output_in_json()
        assert collection_create["name"] == col_name

        indexes_size = len(collection_create["resource"]["indexes"])
        collection_update = self.cmd(
            'az cosmosdb mongodb collection update -g {rg} -a {acc} -d {db_name} -n {col_name} --idx {indexes}').get_output_in_json()
        assert len(collection_update["resource"]["indexes"]) == indexes_size + 1

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

        self.cmd('az cosmosdb mongodb collection delete -g {rg} -a {acc} -d {db_name} -n {col_name} --yes')
        collection_list = self.cmd(
            'az cosmosdb mongodb collection list -g {rg} -a {acc} -d {db_name}').get_output_in_json()
        assert len(collection_list) == 0

        self.cmd('az cosmosdb mongodb collection restore -g {rg} -a {acc} -d {db_name} -n {col_name} --restore-timestamp {rts}').get_output_in_json()

        collection_list = self.cmd(
            'az cosmosdb mongodb collection list -g {rg} -a {acc} -d {db_name}').get_output_in_json()
        assert len(collection_list) == 1

        self.cmd('az cosmosdb mongodb database delete -g {rg} -a {acc} -n {db_name} --yes')
        database_list = self.cmd('az cosmosdb mongodb database list -g {rg} -a {acc}').get_output_in_json()
        assert len(database_list) == 0

        self.cmd('az cosmosdb mongodb database restore -g {rg} -a {acc} -n {db_name} --restore-timestamp {rts}').get_output_in_json()

        database_list = self.cmd('az cosmosdb mongodb database list -g {rg} -a {acc}').get_output_in_json()
        assert len(database_list) == 1

        collection_list = self.cmd(
            'az cosmosdb mongodb collection list -g {rg} -a {acc} -d {db_name}').get_output_in_json()
        assert len(collection_list) == 0

        self.cmd('az cosmosdb mongodb collection restore -g {rg} -a {acc} -d {db_name} -n {col_name} --restore-timestamp {rts}').get_output_in_json()

        import time
        time.sleep(300)

        collection_list = self.cmd(
            'az cosmosdb mongodb collection list -g {rg} -a {acc} -d {db_name}').get_output_in_json()
        assert len(collection_list) == 1

        self.cmd('az cosmosdb mongodb database delete -g {rg} -a {acc} -n {db_name} --yes')
        database_list = self.cmd('az cosmosdb mongodb database list -g {rg} -a {acc}').get_output_in_json()
        assert len(database_list) == 0
        collection_list = self.cmd(
            'az cosmosdb mongodb collection list -g {rg} -a {acc} -d {db_name}').get_output_in_json()
        assert len(collection_list) == 0



    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_mongodb_shared_resources_restore')
    def test_cosmosdb_mongodb_shared_resources_restore(self, resource_group):
        col_name = self.create_random_name(prefix='cli', length=15)
        location = "CentralUS"
        tp1 = 1000
        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'db_name': self.create_random_name(prefix='cli', length=15),
            'col_name': col_name,
            'shard_key': "theShardKey",
            'indexes': '"[{\\"key\\": {\\"keys\\": [\\"_ts\\"]},\\"options\\": {\\"expireAfterSeconds\\": 1000}}]"',
            'loc': location,
            'tp1': tp1
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg} --kind MongoDB --server-version 3.6 --backup-policy-type Continuous --locations regionName={loc}')
        self.cmd('az cosmosdb mongodb database create -g {rg} -a {acc} -n {db_name} --throughput {tp1}')

        assert not self.cmd('az cosmosdb mongodb collection exists -g {rg} -a {acc} -d {db_name} -n {col_name}').get_output_in_json()

        collection_create = self.cmd(
            'az cosmosdb mongodb collection create -g {rg} -a {acc} -d {db_name} -n {col_name} --shard {shard_key}').get_output_in_json()
        assert collection_create["name"] == col_name

        indexes_size = len(collection_create["resource"]["indexes"])
        collection_update = self.cmd(
            'az cosmosdb mongodb collection update -g {rg} -a {acc} -d {db_name} -n {col_name} --idx {indexes}').get_output_in_json()
        assert len(collection_update["resource"]["indexes"]) == indexes_size + 1

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

        self.cmd('az cosmosdb mongodb collection delete -g {rg} -a {acc} -d {db_name} -n {col_name} --yes')
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

        import time
        time.sleep(500)

        self.cmd('az cosmosdb mongodb database restore -g {rg} -a {acc} -n {db_name} --restore-timestamp {rts}').get_output_in_json()

        database_list = self.cmd('az cosmosdb mongodb database list -g {rg} -a {acc}').get_output_in_json()
        assert len(database_list) == 1

        collection_list = self.cmd(
            'az cosmosdb mongodb collection list -g {rg} -a {acc} -d {db_name}').get_output_in_json()
        assert len(collection_list) == 1

        self.cmd('az cosmosdb mongodb database delete -g {rg} -a {acc} -n {db_name} --yes')
        database_list = self.cmd('az cosmosdb mongodb database list -g {rg} -a {acc}').get_output_in_json()
        assert len(database_list) == 0