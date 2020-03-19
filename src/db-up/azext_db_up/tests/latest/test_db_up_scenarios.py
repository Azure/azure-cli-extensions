# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import mock
import psycopg2
import mysql.connector
from azure.cli.testsdk import (ScenarioTest, JMESPathCheck, ResourceGroupPreparer,
                               api_version_constraint, live_only)


class DbUpTests(ScenarioTest):
    @live_only()
    def test_mysql_flow(self):
        group = self.create_random_name(prefix='group', length=24)
        server = self.create_random_name(prefix='server', length=24)

        with mock.patch('azext_db_up.custom._run_mysql_commands'):
            with mock.patch('mysql.connector.connect', side_effect=mysql.connector.errors.DatabaseError()):
                output = self.cmd('mysql up -g {} -s {}'.format(group, server)).get_output_in_json()
                user, server_name = output['username'].split('@')
                password, database = output['password'], 'sampledb'
                self.assertEqual(server, server_name)

                # test followup iterations of up
                self.cmd('mysql up', checks=[JMESPathCheck('password', '*****')])
                self.cmd('mysql up -p {}'.format(password), checks=[JMESPathCheck('password', password)])

        # check that db and server exist
        self.cmd('mysql db show -n {} -g {} -s {}'.format(database, group, server))

        # remove all resources used by up
        self.cmd('mysql down -y --delete-group')

        # check group no longer exists
        with self.assertRaises(SystemExit) as ex:
            self.cmd('group show -n {}'.format(group))
        self.assertEqual(ex.exception.code, 3)

        # check that show-connection-string matches previous output
        output_mirror = self.cmd('mysql show-connection-string -p {} -u {} -d {} -s {}'.format(
            password, user, database, server)).get_output_in_json()
        self.assertEqual(output, output_mirror)

    @live_only()
    def test_postgres_flow(self):
        group = self.create_random_name(prefix='group', length=24)
        server = self.create_random_name(prefix='server', length=24)

        with mock.patch('azext_db_up.custom._run_postgresql_commands'):
            with mock.patch('psycopg2.connect', side_effect=psycopg2.OperationalError()):
                output = self.cmd('postgres up -g {} -s {}'.format(group, server)).get_output_in_json()
                user, server_name = output['username'].split('@')
                password, database = output['password'], 'sampledb'
                self.assertEqual(server, server_name)

                # test followup iterations of up
                self.cmd('postgres up', checks=[JMESPathCheck('password', '*****')])
                self.cmd('postgres up -p {}'.format(password), checks=[JMESPathCheck('password', password)])

        # check that db and server exist
        self.cmd('postgres db show -n {} -g {} -s {}'.format(database, group, server))

        # remove all resources used by up
        self.cmd('postgres down -y --delete-group')

        # check group no longer exists
        with self.assertRaises(SystemExit) as ex:
            self.cmd('group show -n {}'.format(group))
        self.assertEqual(ex.exception.code, 3)

        # check that show-connection-string matches previous output
        output_mirror = self.cmd('postgres show-connection-string -p {} -u {} -d {} -s {}'.format(
            password, user, database, server)).get_output_in_json()
        self.assertEqual(output, output_mirror)

    @live_only()
    @ResourceGroupPreparer(name_prefix='postgresup')
    def test_postgres_up(self, resource_group):
        from ...util import get_config_value, set_config_value
        # Clear all config values
        for item in ['location', 'group', 'server', 'login', 'database']:
            set_config_value('postgres', item, '')

        self.cmd('postgres up')
        rg1 = get_config_value('postgres', 'group')
        server1 = get_config_value('postgres', 'server')

        self.cmd('postgres up -g {}'.format(resource_group))
        rg2 = get_config_value('postgres', 'group')
        server2 = get_config_value('postgres', 'server')
        assert(rg1 != rg2)
        assert(server1 != server2)

    @live_only()  # "sql up" can only run live as updating dependencies is done once during command execution
    def test_sql_flow(self):
        group = self.create_random_name(prefix='group', length=24)
        server = self.create_random_name(prefix='server', length=24)

        output = self.cmd('sql up -g {} -s {}'.format(group, server)).get_output_in_json()
        user, server_name = output['username'].split('@')
        password, database = output['password'], 'sampledb'
        self.assertEqual(server, server_name)

        # test followup iterations of up
        self.cmd('sql up', checks=[JMESPathCheck('password', '*****')])
        self.cmd('sql up -p {}'.format(password), checks=[JMESPathCheck('password', password)])

        # check that db and server exist
        self.cmd('sql db show -n {} -g {} -s {}'.format(database, group, server))

        # remove all resources used by up
        self.cmd('sql down -y --delete-group')

        # check group no longer exists
        with self.assertRaises(SystemExit) as ex:
            self.cmd('group show -n {}'.format(group))
        self.assertEqual(ex.exception.code, 3)
