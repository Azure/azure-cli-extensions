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

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class Cosmosdb_previewPitrScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_gremlin_account_restore_using_create', location='westus2')
    @AllowLargeResponse(size_kb=9999)
    def test_cosmosdb_gremlin_account_restore_using_create(self, resource_group):
        graph = self.create_random_name(prefix='cli', length=15)

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'restored_acc': self.create_random_name(prefix='cli', length=15),
            'db_name': self.create_random_name(prefix='cli', length=15),
            'graph': graph,
            'loc': 'westus2'
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg} --backup-policy-type Continuous --locations regionName={loc} --capabilities EnableGremlin')
        account = self.cmd('az cosmosdb show -n {acc} -g {rg}').get_output_in_json()
        self.cmd('az cosmosdb gremlin database create -g {rg} -a {acc} -n {db_name}')
        self.cmd('az cosmosdb gremlin graph create -g {rg} -a {acc} -d {db_name} -n {graph} -p /pk ').get_output_in_json()

        restorable_accounts_list = self.cmd('az cosmosdb restorable-database-account list').get_output_in_json()
        restorable_database_account = next(acc for acc in restorable_accounts_list if acc['name'] == account['instanceId'])

        account_creation_time = restorable_database_account['creationTime']
        creation_timestamp_datetime = parser.parse(account_creation_time)
        restore_ts = creation_timestamp_datetime + timedelta(minutes=4)
        restore_ts_string = restore_ts.isoformat()
        import time
        time.sleep(240)
        self.kwargs.update({
            'db_id': restorable_database_account['id'],
            'rts': restore_ts_string
        })

        self.cmd('az cosmosdb create -n {restored_acc} -g {rg} --is-restore-request true --restore-source {db_id} --restore-timestamp {rts}')
        restored_account = self.cmd('az cosmosdb show -n {restored_acc} -g {rg}', checks=[
            self.check('restoreParameters.restoreMode', 'PointInTime')
        ]).get_output_in_json()

        assert restored_account['restoreParameters']['restoreSource'] == restorable_database_account['id']
        assert restored_account['restoreParameters']['restoreTimestampInUtc'] == restore_ts_string

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_gremlin_account_restore_command', location='eastus2')
    @AllowLargeResponse(size_kb=9999)
    def test_cosmosdb_gremlin_account_restore_command(self, resource_group):
        graph = self.create_random_name(prefix='cli', length=15)

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'restored_acc': self.create_random_name(prefix='cli', length=15),
            'db_name': self.create_random_name(prefix='cli', length=15),
            'graph': graph,
            'loc': 'eastus2'
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg} --backup-policy-type Continuous --locations regionName={loc} --capabilities EnableGremlin')
        account = self.cmd('az cosmosdb show -n {acc} -g {rg}').get_output_in_json()
        self.kwargs.update({
            'ins_id': account['instanceId']
        })

        self.cmd('az cosmosdb gremlin database create -g {rg} -a {acc} -n {db_name}')
        self.cmd('az cosmosdb gremlin graph create -g {rg} -a {acc} -d {db_name} -n {graph} -p /pk ').get_output_in_json()
        restorable_database_account = self.cmd('az cosmosdb restorable-database-account show --location {loc} --instance-id {ins_id}').get_output_in_json()

        account_creation_time = restorable_database_account['creationTime']
        creation_timestamp_datetime = parser.parse(account_creation_time)
        restore_ts = creation_timestamp_datetime + timedelta(minutes=4)
        import time
        time.sleep(240)
        restore_ts_string = restore_ts.isoformat()
        self.kwargs.update({
            'rts': restore_ts_string
        })

        self.cmd('az cosmosdb restore -n {restored_acc} -g {rg} -a {acc} --restore-timestamp {rts} --location {loc}')
        restored_account = self.cmd('az cosmosdb show -n {restored_acc} -g {rg}', checks=[
            self.check('restoreParameters.restoreMode', 'PointInTime')
        ]).get_output_in_json()

        assert restored_account['restoreParameters']['restoreSource'] == restorable_database_account['id']
        assert restored_account['restoreParameters']['restoreTimestampInUtc'] == restore_ts_string

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_gremlin_restorable_commands', location='eastus2')
    @AllowLargeResponse(size_kb=9999)
    def test_cosmosdb_gremlin_restorable_commands(self, resource_group):
        graph = self.create_random_name(prefix='cli', length=15)
        db_name = self.create_random_name(prefix='cli', length=15)

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'restored_acc': self.create_random_name(prefix='cli', length=15),
            'db_name': db_name,
            'graph': graph,
            'loc': 'eastus2'
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg} --backup-policy-type Continuous --locations regionName={loc} --capabilities EnableGremlin')
        account = self.cmd('az cosmosdb show -n {acc} -g {rg}').get_output_in_json()
        self.kwargs.update({
            'ins_id': account['instanceId']
        })

        self.cmd('az cosmosdb gremlin database create -g {rg} -a {acc} -n {db_name}')
        self.cmd('az cosmosdb gremlin graph create -g {rg} -a {acc} -d {db_name} -n {graph} -p /pk ').get_output_in_json()
        restorable_database_account = self.cmd('az cosmosdb restorable-database-account show --location {loc} --instance-id {ins_id}').get_output_in_json()

        restorable_databases = self.cmd('az cosmosdb gremlin restorable-database list --location {loc} --instance-id {ins_id}').get_output_in_json()
        assert len(restorable_databases) == 1
        restorable_databases[0]['resource']['ownerId'] == db_name

        self.kwargs.update({
            'db_rid': restorable_databases[0]['resource']['ownerResourceId']
        })

        restorable_containers = self.cmd('az cosmosdb gremlin restorable-graph list --location {loc} --instance-id {ins_id} --database-rid {db_rid}').get_output_in_json()
        assert len(restorable_containers) == 1
        assert restorable_containers[0]['resource']['ownerId'] == graph

        account_creation_time = restorable_database_account['creationTime']
        creation_timestamp_datetime = parser.parse(account_creation_time)
        restore_ts = creation_timestamp_datetime + timedelta(minutes=2)
        import time
        time.sleep(120)
        restore_ts_string = restore_ts.isoformat()
        self.kwargs.update({
            'rts': restore_ts_string
        })

        restorable_resources = self.cmd('az cosmosdb gremlin restorable-resource list --restore-location {loc} -l {loc} --instance-id {ins_id} --restore-timestamp {rts}').get_output_in_json()
        assert len(restorable_resources) == 1
        assert restorable_resources[0]['databaseName'] == db_name
        assert len(restorable_resources[0]['graphNames']) == 1
        assert restorable_resources[0]['graphNames'][0] == graph

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_table_account_restore_using_create', location='westus2')
    @AllowLargeResponse(size_kb=9999)
    def test_cosmosdb_table_account_restore_using_create(self, resource_group):
        table = self.create_random_name(prefix='cli', length=15)

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'restored_acc': self.create_random_name(prefix='cli', length=15),
            'table': table,
            'loc': 'westus2'
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg} --backup-policy-type Continuous --locations regionName={loc} --capabilities EnableTable')
        account = self.cmd('az cosmosdb show -n {acc} -g {rg}').get_output_in_json()
        self.cmd('az cosmosdb table create -g {rg} -a {acc} -n {table}').get_output_in_json()

        restorable_accounts_list = self.cmd('az cosmosdb restorable-database-account list').get_output_in_json()
        restorable_database_account = next(acc for acc in restorable_accounts_list if acc['name'] == account['instanceId'])

        account_creation_time = restorable_database_account['creationTime']
        creation_timestamp_datetime = parser.parse(account_creation_time)
        restore_ts = creation_timestamp_datetime + timedelta(minutes=4)
        restore_ts_string = restore_ts.isoformat()
        import time
        time.sleep(240)
        self.kwargs.update({
            'db_id': restorable_database_account['id'],
            'rts': restore_ts_string
        })

        self.cmd('az cosmosdb create -n {restored_acc} -g {rg} --is-restore-request true --restore-source {db_id} --restore-timestamp {rts}')
        restored_account = self.cmd('az cosmosdb show -n {restored_acc} -g {rg}', checks=[
            self.check('restoreParameters.restoreMode', 'PointInTime')
        ]).get_output_in_json()

        assert restored_account['restoreParameters']['restoreSource'] == restorable_database_account['id']
        assert restored_account['restoreParameters']['restoreTimestampInUtc'] == restore_ts_string

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_table_account_restore_command', location='eastus2')
    @AllowLargeResponse(size_kb=9999)
    def test_cosmosdb_table_account_restore_command(self, resource_group):
        table = self.create_random_name(prefix='cli', length=15)

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'restored_acc': self.create_random_name(prefix='cli', length=15),
            'table': table,
            'loc': 'eastus2'
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg} --backup-policy-type Continuous --locations regionName={loc} --capabilities EnableTable')
        account = self.cmd('az cosmosdb show -n {acc} -g {rg}').get_output_in_json()
        self.kwargs.update({
            'ins_id': account['instanceId']
        })

        self.cmd('az cosmosdb table create -g {rg} -a {acc} -n {table}').get_output_in_json()
        restorable_database_account = self.cmd('az cosmosdb restorable-database-account show --location {loc} --instance-id {ins_id}').get_output_in_json()

        account_creation_time = restorable_database_account['creationTime']
        creation_timestamp_datetime = parser.parse(account_creation_time)
        restore_ts = creation_timestamp_datetime + timedelta(minutes=4)
        import time
        time.sleep(240)
        restore_ts_string = restore_ts.isoformat()
        self.kwargs.update({
            'rts': restore_ts_string
        })

        self.cmd('az cosmosdb restore -n {restored_acc} -g {rg} -a {acc} --restore-timestamp {rts} --location {loc}')
        restored_account = self.cmd('az cosmosdb show -n {restored_acc} -g {rg}', checks=[
            self.check('restoreParameters.restoreMode', 'PointInTime')
        ]).get_output_in_json()

        assert restored_account['restoreParameters']['restoreSource'] == restorable_database_account['id']
        assert restored_account['restoreParameters']['restoreTimestampInUtc'] == restore_ts_string

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_table_restorable_commands', location='eastus2')
    @AllowLargeResponse(size_kb=9999)
    def test_cosmosdb_table_restorable_commands(self, resource_group):
        table = self.create_random_name(prefix='cli', length=15)
        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'restored_acc': self.create_random_name(prefix='cli', length=15),
            'table': table,
            'loc': 'eastus2'
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg} --backup-policy-type Continuous --locations regionName={loc} --capabilities EnableTable')
        account = self.cmd('az cosmosdb show -n {acc} -g {rg}').get_output_in_json()
        print(account)
        self.kwargs.update({
            'ins_id': account['instanceId'],
            'throughput': "1000",
        })

        self.cmd('az cosmosdb table create -g {rg} -a {acc} -n {table} --throughput {throughput}').get_output_in_json()

        restorable_database_account = self.cmd('az cosmosdb restorable-database-account show --location {loc} --instance-id {ins_id}').get_output_in_json()

        restorable_containers = self.cmd('az cosmosdb table restorable-table list --location {loc} --instance-id {ins_id}').get_output_in_json()
        assert len(restorable_containers) == 1
        assert restorable_containers[0]['resource']['ownerId'] == table

        account_creation_time = restorable_database_account['creationTime']
        creation_timestamp_datetime = parser.parse(account_creation_time)
        restore_ts = creation_timestamp_datetime + timedelta(minutes=2)
        import time
        time.sleep(120)
        restore_ts_string = restore_ts.isoformat()
        self.kwargs.update({
            'rts': restore_ts_string
        })

        restorable_resources = self.cmd('az cosmosdb table restorable-resource list --restore-location {loc} -l {loc} --instance-id {ins_id} --restore-timestamp {rts}').get_output_in_json()
        assert len(restorable_resources) == 1
        assert len(restorable_resources) == 1
        assert restorable_resources[0]["name"] == table

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_sql_container_backupinfo', location='eastus2')
    def test_cosmosdb_sql_container_backupinfo(self, resource_group):
        col = self.create_random_name(prefix='cli', length=15)
        db_name = self.create_random_name(prefix='cli', length=15)

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'restored_acc': self.create_random_name(prefix='cli', length=15),
            'db_name': db_name,
            'col': col,
            'loc': 'eastus2'
        })

        # This should fail as account doesn't exist
        self.assertRaises(Exception, lambda: self.cmd('az cosmosdb sql retrieve-latest-backup-time -g {rg} -a {acc} -d {db_name} -c {col} -l {loc}'))

        self.cmd('az cosmosdb create -n {acc} -g {rg} --backup-policy-type Continuous --locations regionName={loc} --kind GlobalDocumentDB')
        account = self.cmd('az cosmosdb show -n {acc} -g {rg}').get_output_in_json()

        # This should fail as database doesn't exist
        self.assertRaises(CLIError, lambda: self.cmd('az cosmosdb sql retrieve-latest-backup-time -g {rg} -a {acc} -d {db_name} -c {col} -l {loc}'))

        # Create database
        self.cmd('az cosmosdb sql database create -g {rg} -a {acc} -n {db_name}')

        # This should fail as container doesn't exist
        self.assertRaises(CLIError, lambda: self.cmd('az cosmosdb sql retrieve-latest-backup-time -g {rg} -a {acc} -d {db_name} -c {col} -l {loc}'))

        # Create container
        self.cmd('az cosmosdb sql container create -g {rg} -a {acc} -d {db_name} -n {col} -p /pk ').get_output_in_json()

        backup_info = self.cmd('az cosmosdb sql retrieve-latest-backup-time -g {rg} -a {acc} -d {db_name} -c {col} -l {loc}').get_output_in_json()
        print(backup_info)

        assert backup_info is not None
        assert backup_info['continuousBackupInformation'] is not None

        backup_time = parser.parse(backup_info['continuousBackupInformation']['latestRestorableTimestamp'])

        # Update container
        # container_update = self.cmd('az cosmosdb sql container update -g {rg} -a {acc} -d {db_name} -n {col} --ttl {nttl1}').get_output_in_json()
        # assert container_update["resource"]["defaultTtl"] == 2000

        backup_info = self.cmd('az cosmosdb sql retrieve-latest-backup-time -g {rg} -a {acc} -d {db_name} -c {col} -l {loc}').get_output_in_json()
        print(backup_info)

        assert backup_info is not None
        assert backup_info['continuousBackupInformation'] is not None

        new_backup_time = parser.parse(backup_info['continuousBackupInformation']['latestRestorableTimestamp'])
        assert new_backup_time >= backup_time

        # Update container again
        # container_update = self.cmd('az cosmosdb sql container update -g {rg} -a {acc} -d {db_name} -n {col} --ttl {nttl2}').get_output_in_json()
        # assert container_update["resource"]["defaultTtl"] == 3000

        backup_info = self.cmd('az cosmosdb sql retrieve-latest-backup-time -g {rg} -a {acc} -d {db_name} -c {col} -l {loc}').get_output_in_json()
        print(backup_info)

        assert backup_info is not None
        assert backup_info['continuousBackupInformation'] is not None

        new_backup_time2 = parser.parse(backup_info['continuousBackupInformation']['latestRestorableTimestamp'])
        assert new_backup_time2 >= backup_time
        assert new_backup_time2 >= new_backup_time

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_mongodb_collection_backupinfo', location='eastus2')
    def test_cosmosdb_mongodb_collection_backupinfo(self, resource_group):
        col = self.create_random_name(prefix='cli', length=15)
        db_name = self.create_random_name(prefix='cli', length=15)

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'restored_acc': self.create_random_name(prefix='cli', length=15),
            'db_name': db_name,
            'col': col,
            'loc': 'eastus2',
            'shard_key': "theShardKey",
            'throughput': "1000"
        })

        # This should fail as account doesn't exist
        self.assertRaises(Exception, lambda: self.cmd('az cosmosdb mongodb retrieve-latest-backup-time -g {rg} -a {acc} -d {db_name} -c {col} -l {loc}'))

        self.cmd('az cosmosdb create -n {acc} -g {rg} --backup-policy-type Continuous --locations regionName={loc} --kind MongoDB')
        account = self.cmd('az cosmosdb show -n {acc} -g {rg}').get_output_in_json()

        # This should fail as database doesn't exist
        self.assertRaises(CLIError, lambda: self.cmd('az cosmosdb mongodb retrieve-latest-backup-time -g {rg} -a {acc} -d {db_name} -c {col} -l {loc}'))

        # Create database
        self.cmd('az cosmosdb mongodb database create -g {rg} -a {acc} -n {db_name}')

        # This should fail as collection doesn't exist
        self.assertRaises(CLIError, lambda: self.cmd('az cosmosdb mongodb retrieve-latest-backup-time -g {rg} -a {acc} -d {db_name} -c {col} -l {loc}'))

        # Create collection
        self.cmd('az cosmosdb mongodb collection create -g {rg} -a {acc} -d {db_name} -n {col} --shard {shard_key} --throughput {throughput}').get_output_in_json()

        backup_info = self.cmd('az cosmosdb mongodb retrieve-latest-backup-time -g {rg} -a {acc} -d {db_name} -c {col} -l {loc}').get_output_in_json()
        print(backup_info)

        assert backup_info is not None
        assert backup_info['continuousBackupInformation'] is not None

        backup_time = parser.parse(backup_info['continuousBackupInformation']['latestRestorableTimestamp'])

        # Update collection
        # collection_update = self.cmd('az cosmosdb mongodb collection update -g {rg} -a {acc} -d {db_name} -n {col} --ttl {nttl1}').get_output_in_json()
        # assert collection_update["resource"]["defaultTtl"] == 2000

        backup_info = self.cmd('az cosmosdb mongodb retrieve-latest-backup-time -g {rg} -a {acc} -d {db_name} -c {col} -l {loc}').get_output_in_json()
        print(backup_info)

        assert backup_info is not None
        assert backup_info['continuousBackupInformation'] is not None

        new_backup_time = parser.parse(backup_info['continuousBackupInformation']['latestRestorableTimestamp'])
        assert new_backup_time >= backup_time

        # Update collection again
        # collection_update = self.cmd('az cosmosdb mongodb collection update -g {rg} -a {acc} -d {db_name} -n {col} --ttl {nttl2}').get_output_in_json()
        # assert collection_update["resource"]["defaultTtl"] == 3000

        backup_info = self.cmd('az cosmosdb mongodb retrieve-latest-backup-time -g {rg} -a {acc} -d {db_name} -c {col} -l {loc}').get_output_in_json()
        print(backup_info)

        assert backup_info is not None
        assert backup_info['continuousBackupInformation'] is not None

        new_backup_time2 = parser.parse(backup_info['continuousBackupInformation']['latestRestorableTimestamp'])
        assert new_backup_time2 >= backup_time
        assert new_backup_time2 >= new_backup_time

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_gremlin_graph_backupinfo', location='eastus2')
    def test_cosmosdb_gremlin_graph_backupinfo(self, resource_group):
        graph = self.create_random_name(prefix='cli', length=15)
        db_name = self.create_random_name(prefix='cli', length=15)

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'db_name': db_name,
            'graph': graph,
            'loc': 'eastus2'
        })

        # This should fail as account doesn't exist
        self.assertRaises(Exception, lambda: self.cmd('az cosmosdb gremlin retrieve-latest-backup-time -g {rg} -a {acc} -d {db_name} -n {graph} -l {loc}'))

        self.cmd('az cosmosdb create -n {acc} -g {rg} --backup-policy-type Continuous --locations regionName={loc} --kind GlobalDocumentDB --capabilities EnableGremlin')
        account = self.cmd('az cosmosdb show -n {acc} -g {rg}').get_output_in_json()

        # This should fail as database doesn't exist
        self.assertRaises(CLIError, lambda: self.cmd('az cosmosdb gremlin retrieve-latest-backup-time -g {rg} -a {acc} -d {db_name} -n {graph} -l {loc}'))

        # Create database
        self.cmd('az cosmosdb gremlin database create -g {rg} -a {acc} -n {db_name}')

        # This should fail as container doesn't exist
        self.assertRaises(CLIError, lambda: self.cmd('az cosmosdb gremlin retrieve-latest-backup-time -g {rg} -a {acc} -d {db_name} -n {graph} -l {loc}'))

        # Create container
        self.cmd('az cosmosdb gremlin graph create -g {rg} -a {acc} -d {db_name} -n {graph} -p /pk ').get_output_in_json()

        backup_info = self.cmd('az cosmosdb gremlin retrieve-latest-backup-time -g {rg} -a {acc} -d {db_name} -n {graph} -l {loc}').get_output_in_json()
        print(backup_info)

        assert backup_info is not None
        assert backup_info['continuousBackupInformation'] is not None

        backup_time = parser.parse(backup_info['continuousBackupInformation']['latestRestorableTimestamp'])

        # Update container
        # container_update = self.cmd('az cosmosdb gremlin graph update -g {rg} -a {acc} -d {db_name} -n {graph} --ttl {nttl1}').get_output_in_json()
        # assert container_update["resource"]["defaultTtl"] == 2000

        backup_info = self.cmd('az cosmosdb gremlin retrieve-latest-backup-time -g {rg} -a {acc} -d {db_name} -n {graph} -l {loc}').get_output_in_json()
        print(backup_info)

        assert backup_info is not None
        assert backup_info['continuousBackupInformation'] is not None

        new_backup_time = parser.parse(backup_info['continuousBackupInformation']['latestRestorableTimestamp'])
        assert new_backup_time >= backup_time

        # Update container again
        # container_update = self.cmd('az cosmosdb gremlin graph update -g {rg} -a {acc} -d {db_name} -n {graph} --ttl {nttl2}').get_output_in_json()
        # assert container_update["resource"]["defaultTtl"] == 3000

        backup_info = self.cmd('az cosmosdb gremlin retrieve-latest-backup-time -g {rg} -a {acc} -d {db_name} -n {graph} -l {loc}').get_output_in_json()
        print(backup_info)

        assert backup_info is not None
        assert backup_info['continuousBackupInformation'] is not None

        new_backup_time2 = parser.parse(backup_info['continuousBackupInformation']['latestRestorableTimestamp'])
        assert new_backup_time2 >= backup_time
        assert new_backup_time2 >= new_backup_time

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_table_backupinfo', location='eastus2')
    def test_cosmosdb_table_backupinfo(self, resource_group):
        table = self.create_random_name(prefix='cli', length=15)

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'restored_acc': self.create_random_name(prefix='cli', length=15),
            'table': table,
            'loc': 'eastus2',
            'throughput': "1000"
        })

        # This should fail as account doesn't exist
        self.assertRaises(Exception, lambda: self.cmd('az cosmosdb table retrieve-latest-backup-time -g {rg} -a {acc} -n {table} -l {loc}'))

        self.cmd('az cosmosdb create -n {acc} -g {rg} --backup-policy-type Continuous --locations regionName={loc} --kind GlobalDocumentDB --capabilities EnableTable')
        account = self.cmd('az cosmosdb show -n {acc} -g {rg}').get_output_in_json()

        # This should fail as collection doesn't exist
        self.assertRaises(CLIError, lambda: self.cmd('az cosmosdb table retrieve-latest-backup-time -g {rg} -a {acc} -n {table} -l {loc}'))

        # Create collection
        self.cmd('az cosmosdb table create -g {rg} -a {acc} -n {table} --throughput {throughput}').get_output_in_json()

        backup_info = self.cmd('az cosmosdb table retrieve-latest-backup-time -g {rg} -a {acc} -n {table} -l {loc}').get_output_in_json()
        print(backup_info)

        assert backup_info is not None
        assert backup_info['continuousBackupInformation'] is not None

        backup_time = parser.parse(backup_info['continuousBackupInformation']['latestRestorableTimestamp'])

        # Update collection
        # collection_update = self.cmd('az cosmosdb table update -g {rg} -a {acc} -n {table} --ttl {nttl1}').get_output_in_json()
        # assert collection_update["resource"]["defaultTtl"] == 2000

        backup_info = self.cmd('az cosmosdb table retrieve-latest-backup-time -g {rg} -a {acc} -n {table} -l {loc}').get_output_in_json()
        print(backup_info)

        assert backup_info is not None
        assert backup_info['continuousBackupInformation'] is not None

        new_backup_time = parser.parse(backup_info['continuousBackupInformation']['latestRestorableTimestamp'])
        assert new_backup_time >= backup_time

        # Update collection again
        # collection_update = self.cmd('az cosmosdb table update -g {rg} -a {acc} -n {table} --ttl {nttl2}').get_output_in_json()
        # assert collection_update["resource"]["defaultTtl"] == 3000

        backup_info = self.cmd('az cosmosdb table retrieve-latest-backup-time -g {rg} -a {acc} -n {table} -l {loc}').get_output_in_json()
        print(backup_info)

        assert backup_info is not None
        assert backup_info['continuousBackupInformation'] is not None

        new_backup_time2 = parser.parse(backup_info['continuousBackupInformation']['latestRestorableTimestamp'])
        assert new_backup_time2 >= backup_time
        assert new_backup_time2 >= new_backup_time

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_sql_provision_continuous7days', location='eastus2')
    def test_cosmosdb_sql_continuous7days(self, resource_group):
        col = self.create_random_name(prefix='cli', length=15)
        db_name = self.create_random_name(prefix='cli', length=15)

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli-continuous7-', length=25),
            'db_name': db_name,
            'col': col,
            'loc': 'eastus2'
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg} --backup-policy-type Continuous --continuous-tier Continuous7Days --locations regionName={loc} --kind GlobalDocumentDB')
        account = self.cmd('az cosmosdb show -n {acc} -g {rg}').get_output_in_json()
        print(account)

        assert account is not None
        assert account['backupPolicy'] is not None
        assert account['backupPolicy']['continuousModeProperties'] is not None

        continuous_tier = account['backupPolicy']['continuousModeProperties']['tier']
        assert continuous_tier == 'Continuous7Days'

        self.cmd('az cosmosdb update -n {acc} -g {rg} --backup-policy-type Continuous --continuous-tier Continuous30Days')
        updated_account = self.cmd('az cosmosdb show -n {acc} -g {rg}').get_output_in_json()
        print(updated_account)

        assert updated_account is not None
        assert updated_account['backupPolicy'] is not None
        assert updated_account['backupPolicy']['continuousModeProperties'] is not None

        updated_continuous_tier = updated_account['backupPolicy']['continuousModeProperties']['tier']
        assert updated_continuous_tier == 'Continuous30Days'

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_sql_provision_continuous30days', location='eastus2')
    def test_cosmosdb_sql_continuous30days(self, resource_group):
        col = self.create_random_name(prefix='cli', length=15)
        db_name = self.create_random_name(prefix='cli', length=15)

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli-continuous30-', length=25),
            'db_name': db_name,
            'col': col,
            'loc': 'eastus2'
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg} --backup-policy-type Continuous --locations regionName={loc} --kind GlobalDocumentDB')
        account = self.cmd('az cosmosdb show -n {acc} -g {rg}').get_output_in_json()
        print(account)

        assert account is not None
        assert account['backupPolicy'] is not None
        assert account['backupPolicy']['continuousModeProperties'] is not None

        continuous_tier = account['backupPolicy']['continuousModeProperties']['tier']

        # If continuous tier is not provided, then it's default to Continuous30Days
        assert continuous_tier == 'Continuous30Days'

        self.cmd('az cosmosdb update -n {acc} -g {rg} --backup-policy-type Continuous --continuous-tier Continuous7Days')
        updated_account = self.cmd('az cosmosdb show -n {acc} -g {rg}').get_output_in_json()
        print(updated_account)

        assert updated_account is not None
        assert updated_account['backupPolicy'] is not None
        assert updated_account['backupPolicy']['continuousModeProperties'] is not None

        updated_continuous_tier = updated_account['backupPolicy']['continuousModeProperties']['tier']
        assert updated_continuous_tier == 'Continuous7Days'

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_sql_migrate_periodic_to_continuous7days', location='eastus2')
    def test_cosmosdb_sql_migrate_periodic_to_continuous7days(self, resource_group):
        col = self.create_random_name(prefix='cli', length=15)
        db_name = self.create_random_name(prefix='cli', length=15)

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli-periodic-', length=25),
            'db_name': db_name,
            'col': col,
            'loc': 'eastus2'
        })

        # Create periodic backup account (by default is --backup-policy-type is not specified, then it is a Periodic account)
        self.cmd('az cosmosdb create -n {acc} -g {rg} --locations regionName={loc} --kind GlobalDocumentDB')
        account = self.cmd('az cosmosdb show -n {acc} -g {rg}').get_output_in_json()
        print(account)

        assert account is not None
        assert account['backupPolicy'] is not None
        assert account['backupPolicy']['periodicModeProperties'] is not None

        # Migrate periodic account to Continuous 7 days
        self.cmd('az cosmosdb update -n {acc} -g {rg} --backup-policy-type Continuous --continuous-tier Continuous7Days')
        updated_account = self.cmd('az cosmosdb show -n {acc} -g {rg}').get_output_in_json()
        print(updated_account)

        assert updated_account is not None
        assert updated_account['backupPolicy'] is not None
        assert updated_account['backupPolicy']['continuousModeProperties'] is not None

        updated_continuous_tier = updated_account['backupPolicy']['continuousModeProperties']['tier']
        assert updated_continuous_tier == 'Continuous7Days'

        # Update account to Continuous 30 days
        self.cmd('az cosmosdb update -n {acc} -g {rg} --backup-policy-type Continuous --continuous-tier Continuous30Days')
        updated_account = self.cmd('az cosmosdb show -n {acc} -g {rg}').get_output_in_json()
        print(updated_account)

        assert updated_account is not None
        assert updated_account['backupPolicy'] is not None
        assert updated_account['backupPolicy']['continuousModeProperties'] is not None

        updated_continuous_tier = updated_account['backupPolicy']['continuousModeProperties']['tier']
        assert updated_continuous_tier == 'Continuous30Days'

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_sql_oldestRestorableTime', location='eastus2')
    def test_cosmosdb_sql_oldestRestorableTime(self, resource_group):
        col = self.create_random_name(prefix='cli', length=15)
        db_name = self.create_random_name(prefix='cli', length=15)

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli-continuous7-', length=25),
            'db_name': db_name,
            'col': col,
            'loc': 'eastus2'
        })

        # Create periodic backup account (by default is --backup-policy-type is not specified, then it is a Periodic account)
        self.cmd('az cosmosdb create -n {acc} -g {rg} --backup-policy-type Continuous --continuous-tier Continuous7Days --locations regionName={loc} --kind GlobalDocumentDB')
        account = self.cmd('az cosmosdb show -n {acc} -g {rg}').get_output_in_json()
        print(account)

        self.cmd('az cosmosdb create -n {acc} -g {rg} --backup-policy-type Continuous --continuous-tier Continuous7Days --locations regionName={loc} --kind GlobalDocumentDB')
        account = self.cmd('az cosmosdb show -n {acc} -g {rg}').get_output_in_json()
        self.kwargs.update({
            'ins_id': account['instanceId']
        })

        restorable_database_account_show = self.cmd('az cosmosdb restorable-database-account show --location {loc} --instance-id {ins_id}').get_output_in_json()
        account_oldest_restorable_time = restorable_database_account_show['oldestRestorableTime']
        assert account_oldest_restorable_time is not None

        restorable_accounts_list = self.cmd('az cosmosdb restorable-database-account list').get_output_in_json()
        restorable_database_account = next(acc for acc in restorable_accounts_list if acc['name'] == account['instanceId'])
        account_oldest_restorable_time = restorable_database_account['oldestRestorableTime']
        assert account_oldest_restorable_time is not None