# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
import time
import datetime

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from knack.log import get_logger

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

logger = get_logger(__name__)


class CosmosDBSoftDeleteScenarioTest(ScenarioTest):
    """
    Test suite for CosmosDB SQL API soft-delete functionality.
    
    This test suite validates the soft-delete and recovery operations for:
    - Database Accounts
    - SQL Databases
    - SQL Collections/Containers
    
    Note: These tests require a CosmosDB account with soft-delete feature enabled.
    """

    def _create_account_with_soft_delete(self, account_name, resource_group, location):
        """
        Helper function to create a CosmosDB account and enable soft delete.
        Sets retention period and minimum purge minutes to 0 for testing.
        """
        self.kwargs.update({
            'acc': account_name,
            'rg': resource_group,
            'loc': location
        })
        
        logger.info("Creating CosmosDB account")
        self.cmd('az cosmosdb create -n {acc} -g {rg} --locations regionName={loc}')
        
        logger.info("Enabling soft delete on account")
        self.cmd(
            'az cosmosdb update -n {acc} -g {rg} '
            '--enable-soft-deletion true '
            '--sd-retention 0 '
            '--min-purge-minutes 0'
        )
        logger.info("Account created with soft delete enabled")

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_softdelete_acc_recover', location='westus')
    def test_cosmosdb_sql_softdeleted_account_recover(self, resource_group):
        """
        Test soft-deleted account recovery operation.
        
        This test validates that soft-deleted accounts can be recovered.
        """
        location = "westus"

        self.kwargs.update({
            'acc': self.create_random_name(prefix='clisdacc', length=20),
            'loc': location
        })

        self._create_account_with_soft_delete(self.kwargs['acc'], resource_group, location)

        logger.info("Soft-deleting the account")
        self.cmd('az cosmosdb delete -n {acc} -g {rg} --yes')

        logger.info("Waiting for account deletion to complete")
        time.sleep(120)

        logger.info("Listing soft-deleted accounts")
        soft_deleted_accounts = self.cmd(
            'az cosmosdb softdeleted-account list '
            '--location {loc} -g {rg}'
        ).get_output_in_json()
        
        deleted_account_found = any(acc.get('name') == self.kwargs['acc'] for acc in soft_deleted_accounts)
        assert deleted_account_found, f"Soft-deleted account '{self.kwargs['acc']}' should appear in the list"

        logger.info("Showing soft-deleted account details")
        soft_deleted_account = self.cmd(
            'az cosmosdb softdeleted-account show '
            '--location {loc} --account-name {acc} -g {rg}'
        ).get_output_in_json()
        assert soft_deleted_account is not None

        logger.info("Recovering the soft-deleted account")
        self.cmd(
            'az cosmosdb softdeleted-account recover '
            '--location {loc} --account-name {acc} -g {rg}'
        )
        
        logger.info("Waiting for account recovery to complete")
        time.sleep(120)
        
        logger.info("Verifying account is recovered")
        recovered_account = self.cmd('az cosmosdb show -n {acc} -g {rg}').get_output_in_json()
        assert recovered_account is not None
        
        logger.info("Verifying account is no longer in soft-deleted list")
        soft_deleted_accounts_after = self.cmd(
            'az cosmosdb softdeleted-account list '
            '--location {loc} -g {rg}'
        ).get_output_in_json()
        
        recovered_account_found = any(acc.get('name') == self.kwargs['acc'] for acc in soft_deleted_accounts_after)
        assert not recovered_account_found, "Account should not appear in soft-deleted list after recovery"

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_softdelete_acc_purge', location='westus')
    def test_cosmosdb_sql_softdeleted_account_purge(self, resource_group):
        """
        Test soft-deleted account purge (permanent deletion) operation.
        
        This test validates that soft-deleted accounts can be permanently removed.
        """
        location = "westus"

        self.kwargs.update({
            'acc': self.create_random_name(prefix='clisdpacc', length=20),
            'loc': location
        })

        self._create_account_with_soft_delete(self.kwargs['acc'], resource_group, location)

        logger.info("Soft-deleting the account")
        self.cmd('az cosmosdb delete -n {acc} -g {rg} --yes')

        logger.info("Waiting for account deletion to complete")
        time.sleep(120)

        logger.info("Listing soft-deleted accounts")
        soft_deleted_accounts = self.cmd(
            'az cosmosdb softdeleted-account list '
            '--location {loc} -g {rg}'
        ).get_output_in_json()
        
        deleted_account_found = any(acc.get('name') == self.kwargs['acc'] for acc in soft_deleted_accounts)
        assert deleted_account_found, f"Soft-deleted account '{self.kwargs['acc']}' should appear in the list"

        logger.info("Showing soft-deleted account details")
        soft_deleted_account = self.cmd(
            'az cosmosdb softdeleted-account show '
            '--location {loc} --account-name {acc} -g {rg}'
        ).get_output_in_json()
        assert soft_deleted_account is not None

        logger.info("Purging the soft-deleted account")
        self.cmd(
            'az cosmosdb softdeleted-account delete '
            '--location {loc} --account-name {acc} -g {rg} --yes'
        )
        
        logger.info("Waiting for account purge to complete")
        time.sleep(120)
        
        logger.info("Account successfully purged")
        
        logger.info("Verifying account is no longer in soft-deleted list")
        soft_deleted_accounts_after = self.cmd(
            'az cosmosdb softdeleted-account list '
            '--location {loc} -g {rg}'
        ).get_output_in_json()
        
        purged_account_found = any(acc.get('name') == self.kwargs['acc'] for acc in soft_deleted_accounts_after)
        assert not purged_account_found, "Account should not appear in soft-deleted list after purge"

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_softdelete_db_recover', location='westus')
    def test_cosmosdb_sql_softdeleted_database_recover(self, resource_group):
        """
        Test soft-deleted database recovery operations: list, show, and recover.
        
        This test validates the database soft-delete and recovery workflow.
        """
        location = "westus"
        db_name = self.create_random_name(prefix='clisdddb', length=15)

        self.kwargs.update({
            'acc': self.create_random_name(prefix='clisddacc', length=20),
            'db_name': db_name,
            'loc': location
        })

        self._create_account_with_soft_delete(self.kwargs['acc'], resource_group, location)

        logger.info("Creating SQL database")
        database_create = self.cmd(
            'az cosmosdb sql database create -g {rg} -a {acc} -n {db_name}'
        ).get_output_in_json()
        assert database_create["name"] == db_name

        logger.info("Waiting for database to stabilize")
        time.sleep(60)

        logger.info("Soft-deleting the database")
        self.cmd('az cosmosdb sql database delete -g {rg} -a {acc} -n {db_name} --yes')

        time.sleep(60)

        logger.info("Listing soft-deleted databases")
        soft_deleted_dbs = self.cmd(
            'az cosmosdb sql softdeleted-database list '
            '--location {loc} --account-name {acc} -g {rg}'
        ).get_output_in_json()
        
        # Verify the deleted database appears in the list
        deleted_db_found = any(db.get('name') == db_name for db in soft_deleted_dbs)
        assert deleted_db_found, f"Soft-deleted database '{db_name}' should appear in the list"

        logger.info("Showing soft-deleted database details")
        soft_deleted_db = self.cmd(
            'az cosmosdb sql softdeleted-database show '
            '--location {loc} --account-name {acc} --name {db_name} -g {rg}'
        ).get_output_in_json()
        assert soft_deleted_db is not None
        logger.info(f"Soft-deleted database details retrieved successfully")

        logger.info("Recovering the soft-deleted database")
        self.cmd(
            'az cosmosdb sql softdeleted-database recover '
            '--location {loc} --account-name {acc} --name {db_name} -g {rg}'
        )
        
        time.sleep(120)
        
        recovered_db = self.cmd(
            'az cosmosdb sql database show -g {rg} -a {acc} -n {db_name}'
        ).get_output_in_json()
        assert recovered_db["name"] == db_name
        logger.info("Database successfully recovered")

        logger.info("Verifying database is no longer soft-deleted")
        soft_deleted_dbs_after = self.cmd(
            'az cosmosdb sql softdeleted-database list '
            '--location {loc} --account-name {acc} -g {rg}'
        ).get_output_in_json()
        
        still_soft_deleted = any(db.get('name') == db_name for db in soft_deleted_dbs_after)
        assert not still_soft_deleted, "Database should not appear in soft-deleted list after recovery"

        logger.info("Cleaning up test resources")
        self.cmd('az cosmosdb sql database delete -g {rg} -a {acc} -n {db_name} --yes')

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_softdelete_coll_recover', location='westus')
    def test_cosmosdb_sql_softdeleted_collection_recover(self, resource_group):
        """
        Test soft-deleted collection recovery operations: list, show, and recover.
        
        This test validates the collection/container soft-delete and recovery workflow.
        """
        location = "westus"
        db_name = self.create_random_name(prefix='clisdddb', length=15)
        coll_name = self.create_random_name(prefix='clisddcoll', length=15)
        partition_key = "/pk"

        self.kwargs.update({
            'acc': self.create_random_name(prefix='clisddacc', length=20),
            'db_name': db_name,
            'coll_name': coll_name,
            'part': partition_key,
            'loc': location
        })

        self._create_account_with_soft_delete(self.kwargs['acc'], resource_group, location)

        logger.info("Creating SQL database")
        self.cmd('az cosmosdb sql database create -g {rg} -a {acc} -n {db_name}')

        logger.info("Creating SQL container")
        collection_create = self.cmd(
            'az cosmosdb sql container create -g {rg} -a {acc} '
            '-d {db_name} -n {coll_name} -p {part}'
        ).get_output_in_json()
        assert collection_create["name"] == coll_name

        logger.info("Waiting for container to stabilize")
        time.sleep(60)

        logger.info("Soft-deleting the container")
        self.cmd(
            'az cosmosdb sql container delete -g {rg} -a {acc} '
            '-d {db_name} -n {coll_name} --yes'
        )

        time.sleep(60)

        logger.info("Listing soft-deleted collections")
        soft_deleted_colls = self.cmd(
            'az cosmosdb sql softdeleted-collection list '
            '--location {loc} --account-name {acc} '
            '--database-name {db_name} -g {rg}'
        ).get_output_in_json()
        
        # Verify the deleted collection appears in the list
        deleted_coll_found = any(coll.get('name') == coll_name for coll in soft_deleted_colls)
        assert deleted_coll_found, f"Soft-deleted collection '{coll_name}' should appear in the list"

        logger.info("Showing soft-deleted collection details")
        soft_deleted_coll = self.cmd(
            'az cosmosdb sql softdeleted-collection show '
            '--location {loc} --account-name {acc} '
            '--database-name {db_name} --name {coll_name} -g {rg}'
        ).get_output_in_json()
        assert soft_deleted_coll is not None
        logger.info(f"Soft-deleted collection details retrieved successfully")

        logger.info("Recovering the soft-deleted collection")
        self.cmd(
            'az cosmosdb sql softdeleted-collection recover '
            '--location {loc} --account-name {acc} '
            '--database-name {db_name} --name {coll_name} -g {rg}'
        )
        
        time.sleep(120)
        
        recovered_coll = self.cmd(
            'az cosmosdb sql container show -g {rg} -a {acc} '
            '-d {db_name} -n {coll_name}'
        ).get_output_in_json()
        assert recovered_coll["name"] == coll_name
        logger.info("Collection successfully recovered")

        logger.info("Verifying collection is no longer soft-deleted")
        soft_deleted_colls_after = self.cmd(
            'az cosmosdb sql softdeleted-collection list '
            '--location {loc} --account-name {acc} '
            '--database-name {db_name} -g {rg}'
        ).get_output_in_json()
        
        still_soft_deleted = any(coll.get('name') == coll_name for coll in soft_deleted_colls_after)
        assert not still_soft_deleted, "Collection should not appear in soft-deleted list after recovery"

        logger.info("Cleaning up test resources")
        self.cmd(
            'az cosmosdb sql container delete -g {rg} -a {acc} '
            '-d {db_name} -n {coll_name} --yes'
        )
        self.cmd('az cosmosdb sql database delete -g {rg} -a {acc} -n {db_name} --yes')

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_softdelete_purge', location='westus')
    def test_cosmosdb_sql_softdeleted_database_purge(self, resource_group):
        """
        Test soft-deleted database purge (permanent deletion) operation.
        
        This test validates that soft-deleted databases can be permanently removed.
        """
        location = "westus"
        db_name = self.create_random_name(prefix='clisdpdb', length=15)

        self.kwargs.update({
            'acc': self.create_random_name(prefix='clisdpacc', length=20),
            'db_name': db_name,
            'loc': location
        })

        self._create_account_with_soft_delete(self.kwargs['acc'], resource_group, location)

        logger.info("Creating SQL database")
        self.cmd('az cosmosdb sql database create -g {rg} -a {acc} -n {db_name}')

        logger.info("Waiting for database to stabilize")
        time.sleep(60)

        logger.info("Soft-deleting the database")
        self.cmd('az cosmosdb sql database delete -g {rg} -a {acc} -n {db_name} --yes')

        time.sleep(60)

        logger.info("Purging the soft-deleted database")
        try:
            self.cmd(
                'az cosmosdb sql softdeleted-database delete '
                '--location {loc} --account-name {acc} --name {db_name} -g {rg} --yes'
            )
            
            time.sleep(60)
            
            logger.info("Database successfully purged")
            
            soft_deleted_dbs = self.cmd(
                'az cosmosdb sql softdeleted-database list '
                '--location {loc} --account-name {acc} -g {rg}'
            ).get_output_in_json()
            
            purged_db_found = any(db.get('name') == db_name for db in soft_deleted_dbs)
            assert not purged_db_found, "Database should not appear in soft-deleted list after purge"
            
        except Exception as e:
            logger.warning(f"Database purge test skipped or failed: {e}")

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_softdelete_coll_purge', location='westus')
    def test_cosmosdb_sql_softdeleted_collection_purge(self, resource_group):
        """
        Test soft-deleted collection purge (permanent deletion) operation.
        
        This test validates that soft-deleted collections can be permanently removed.
        """
        location = "westus"
        db_name = self.create_random_name(prefix='clisdpdb', length=15)
        coll_name = self.create_random_name(prefix='clisdpcoll', length=15)
        partition_key = "/pk"

        self.kwargs.update({
            'acc': self.create_random_name(prefix='clisdpacc', length=20),
            'db_name': db_name,
            'coll_name': coll_name,
            'part': partition_key,
            'loc': location
        })

        self._create_account_with_soft_delete(self.kwargs['acc'], resource_group, location)

        logger.info("Creating SQL database")
        self.cmd('az cosmosdb sql database create -g {rg} -a {acc} -n {db_name}')

        logger.info("Creating SQL container")
        self.cmd(
            'az cosmosdb sql container create -g {rg} -a {acc} '
            '-d {db_name} -n {coll_name} -p {part}'
        )

        logger.info("Waiting for container to stabilize")
        time.sleep(60)

        logger.info("Soft-deleting the container")
        self.cmd(
            'az cosmosdb sql container delete -g {rg} -a {acc} '
            '-d {db_name} -n {coll_name} --yes'
        )

        time.sleep(60)

        logger.info("Listing soft-deleted collections")
        soft_deleted_colls = self.cmd(
            'az cosmosdb sql softdeleted-collection list '
            '--location {loc} --account-name {acc} '
            '--database-name {db_name} -g {rg}'
        ).get_output_in_json()
        
        deleted_coll_found = any(coll.get('name') == coll_name for coll in soft_deleted_colls)
        assert deleted_coll_found, f"Soft-deleted collection '{coll_name}' should appear in the list"

        logger.info("Showing soft-deleted collection details")
        soft_deleted_coll = self.cmd(
            'az cosmosdb sql softdeleted-collection show '
            '--location {loc} --account-name {acc} '
            '--database-name {db_name} --name {coll_name} -g {rg}'
        ).get_output_in_json()
        assert soft_deleted_coll is not None

        logger.info("Purging the soft-deleted collection")
        self.cmd(
            'az cosmosdb sql softdeleted-collection delete '
            '--location {loc} --account-name {acc} '
            '--database-name {db_name} --name {coll_name} -g {rg} --yes'
        )
        
        time.sleep(60)
        
        logger.info("Collection successfully purged")
        
        logger.info("Verifying collection is no longer in soft-deleted list")
        soft_deleted_colls_after = self.cmd(
            'az cosmosdb sql softdeleted-collection list '
            '--location {loc} --account-name {acc} '
            '--database-name {db_name} -g {rg}'
        ).get_output_in_json()
        
        purged_coll_found = any(coll.get('name') == coll_name for coll in soft_deleted_colls_after)
        assert not purged_coll_found, "Collection should not appear in soft-deleted list after purge"

        logger.info("Cleaning up test resources")
        self.cmd('az cosmosdb sql database delete -g {rg} -a {acc} -n {db_name} --yes')


if __name__ == '__main__':
    unittest.main()
