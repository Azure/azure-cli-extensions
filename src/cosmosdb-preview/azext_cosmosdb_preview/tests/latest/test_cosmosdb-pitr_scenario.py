# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class Cosmosdb_previewScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_update_backup_policy_database_account')
    def test_update_backup_policy_database_account(self):

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=40)
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg}')
        self.cmd('az cosmosdb show -n {acc} -g {rg}', checks=[
            self.check('backupPolicy.type', 'Periodic')
        ])

        self.cmd('az cosmosdb update -n {acc} -g {rg} --backup-interval 120 --backup-retention 8', checks=[
            self.check('backupPolicy.periodicModeProperties.backupIntervalInMinutes', '120'),
            self.check('backupPolicy.periodicModeProperties.backupRetentionIntervalInHours', '8'),
            self.check('backupPolicy.type', 'Periodic'),
        ])

    @ResourceGroupPreparer(name_prefix='cli_update_pitrmigrate_database_account')
    def test_update_pitrmigrate_database_account(self):

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=40)
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg}')
        self.cmd('az cosmosdb show -n {acc} -g {rg}', checks=[
            self.check('backupPolicy.type', 'Periodic')
        ])

        self.cmd('az cosmosdb update -n {acc} -g {rg} --backup-policy-type continuous', checks=[
            self.check('backupPolicy.type', 'Continuous'),
        ])

    # pylint: disable=line-too-long
    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_restore_using_create', parameter_name_for_location='location')
    def test_cosmosdb_restore_using_create(self, location):
        col = self.create_random_name(prefix='cli', length=15)

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'restored_acc': self.create_random_name(prefix='cli', length=15),
            'db_name': self.create_random_name(prefix='cli', length=15),
            'col': col,
            'loc': location
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg} --backup-policy-type Continuous --locations regionName={loc}')
        account = self.cmd('az cosmosdb show -n {acc} -g {rg}').get_output_in_json()
        self.cmd('az cosmosdb sql database create -g {rg} -a {acc} -n {db_name}')
        self.cmd('az cosmosdb sql container create -g {rg} -a {acc} -d {db_name} -n {col} -p /pk ').get_output_in_json()

        restorable_accounts_list = self.cmd('az cosmosdb restorable-database-account list').get_output_in_json()
        restorable_database_account = next(
            acc for acc in restorable_accounts_list if acc['name'] == account['instanceId'])

        account_creation_time = restorable_database_account['creationTime']
        import dateutil
        from datetime import timedelta
        creation_timestamp_datetime = dateutil.parser.parse(account_creation_time)
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

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_restore_command', parameter_name_for_location='location')
    def test_cosmosdb_restore_command(self, location):
        col = self.create_random_name(prefix='cli', length=15)

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'restored_acc': self.create_random_name(prefix='cli', length=15),
            'db_name': self.create_random_name(prefix='cli', length=15),
            'col': col,
            'loc': location
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg} --backup-policy-type Continuous --locations regionName={loc}')
        account = self.cmd('az cosmosdb show -n {acc} -g {rg}').get_output_in_json()
        self.kwargs.update({
            'ins_id': account['instanceId']
        })

        self.cmd('az cosmosdb sql database create -g {rg} -a {acc} -n {db_name}')
        self.cmd('az cosmosdb sql container create -g {rg} -a {acc} -d {db_name} -n {col} -p /pk ').get_output_in_json()
        restorable_database_account = self.cmd(
            'az cosmosdb restorable-database-account show --location {loc} --instance-id {ins_id}').get_output_in_json()

        account_creation_time = restorable_database_account['creationTime']
        import dateutil
        from datetime import timedelta
        creation_timestamp_datetime = dateutil.parser.parse(account_creation_time)
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

    # pylint: disable=line-too-long
    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_sql_restorable_commands', parameter_name_for_location='location')
    def test_cosmosdb_sql_restorable_commands(self, location):
        col = self.create_random_name(prefix='cli', length=15)
        db_name = self.create_random_name(prefix='cli', length=15)

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'restored_acc': self.create_random_name(prefix='cli', length=15),
            'db_name': db_name,
            'col': col,
            'loc': location
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg} --backup-policy-type Continuous --locations regionName={loc}')
        account = self.cmd('az cosmosdb show -n {acc} -g {rg}').get_output_in_json()
        self.kwargs.update({
            'ins_id': account['instanceId']
        })

        self.cmd('az cosmosdb sql database create -g {rg} -a {acc} -n {db_name}')
        self.cmd('az cosmosdb sql container create -g {rg} -a {acc} -d {db_name} -n {col} -p /pk ').get_output_in_json()
        restorable_database_account = self.cmd(
            'az cosmosdb restorable-database-account show --location {loc} --instance-id {ins_id}').get_output_in_json()

        restorable_databases = self.cmd('az cosmosdb sql restorable-database list --location {loc} --instance-id {ins_id}').get_output_in_json()
        assert len(restorable_databases) == 1

        self.kwargs.update({
            'db_rid': restorable_databases[0]['resource']['ownerResourceId']
        })

        restorable_containers = self.cmd('az cosmosdb sql restorable-container list --location {loc} --instance-id {ins_id} --database-rid {db_rid}').get_output_in_json()
        assert len(restorable_containers) == 1
        assert restorable_containers[0]['resource']['ownerId'] == col

        account_creation_time = restorable_database_account['creationTime']
        import dateutil
        from datetime import timedelta
        creation_timestamp_datetime = dateutil.parser.parse(account_creation_time)
        restore_ts = creation_timestamp_datetime + timedelta(minutes=2)
        import time
        time.sleep(120)
        restore_ts_string = restore_ts.isoformat()
        self.kwargs.update({
            'rts': restore_ts_string
        })

        restorable_resources = self.cmd('az cosmosdb sql restorable-resource list --restore-location {loc} -l {loc} --instance-id {ins_id} --restore-timestamp {rts}').get_output_in_json()
        assert len(restorable_resources) == 1
        assert restorable_resources[0]['databaseName'] == db_name
        assert len(restorable_resources[0]['collectionNames']) == 1
        assert restorable_resources[0]['collectionNames'][0] == col

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_mongodb_restorable_commands', parameter_name_for_location='location')
    def test_cosmosdb_mongodb_restorable_commands(self, location):
        col = self.create_random_name(prefix='cli', length=15)
        db_name = self.create_random_name(prefix='cli', length=15)
        print(col)
        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'restored_acc': self.create_random_name(prefix='cli', length=15),
            'db_name': db_name,
            'col': col,
            'loc': location
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg} --backup-policy-type Continuous --locations regionName={loc} --kind MongoDB')
        account = self.cmd('az cosmosdb show -n {acc} -g {rg}').get_output_in_json()
        print(account)
        self.kwargs.update({
            'ins_id': account['instanceId'],
            'shard_key': "theShardKey",
            'throughput': "1000",
        })

        self.cmd('az cosmosdb mongodb database create -g {rg} -a {acc} -n {db_name}')
        self.cmd('az cosmosdb mongodb collection create -g {rg} -a {acc} -d {db_name} -n {col} --shard {shard_key} --throughput {throughput}').get_output_in_json()

        restorable_database_account = self.cmd('az cosmosdb restorable-database-account show --location {loc} --instance-id {ins_id}').get_output_in_json()

        restorable_databases = self.cmd('az cosmosdb mongodb restorable-database list --location {loc} --instance-id {ins_id}').get_output_in_json()
        assert len(restorable_databases) == 1

        self.kwargs.update({
            'db_rid': restorable_databases[0]['resource']['ownerResourceId']
        })

        restorable_containers = self.cmd('az cosmosdb mongodb restorable-collection list --location {loc} --instance-id {ins_id} --database-rid {db_rid}').get_output_in_json()
        assert len(restorable_containers) == 1
        assert restorable_containers[0]['resource']['ownerId'] == col

        account_creation_time = restorable_database_account['creationTime']
        import dateutil
        from datetime import timedelta
        creation_timestamp_datetime = dateutil.parser.parse(account_creation_time)
        restore_ts = creation_timestamp_datetime + timedelta(minutes=2)
        import time
        time.sleep(120)
        restore_ts_string = restore_ts.isoformat()
        self.kwargs.update({
            'rts': restore_ts_string
        })

        restorable_resources = self.cmd('az cosmosdb mongodb restorable-resource list --restore-location {loc} -l {loc} --instance-id {ins_id} --restore-timestamp {rts}').get_output_in_json()
        assert len(restorable_resources) == 1
        assert restorable_resources[0]['databaseName'] == db_name
        assert len(restorable_resources[0]['collectionNames']) == 1
        assert restorable_resources[0]['collectionNames'][0] == col
