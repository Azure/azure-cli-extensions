# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from unittest import mock

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck)

from azext_staticwebapp.custom import create_dbconnection
from azext_staticwebapp._utils import MySqlFlexHandler, PgSqlFlexHandler


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class StaticwebappDbConnectionScenarioTest(ScenarioTest):
    @ResourceGroupPreparer(name_prefix='cli_test')
    def test_staticwebapp_dbconnection_azure_sql(self, resource_group):
        name = self.create_random_name("cli_test", length=20)
        server = self.create_random_name("cli-test", length=20)
        username = "aturing"
        password = "thisisapassword123!"
        location = "West US"
        db_name = "tables"

        self.cmd(f"staticwebapp create -n {name} -g {resource_group} -l centralus")
        server_id = self.cmd(f"sql server create -l '{location}' -g {resource_group} -n {server} -u {username} -p {password}").get_output_in_json()["id"]
        self.cmd(f"sql db create -g {resource_group} -n {db_name} -s {server}")

        self.cmd(f"staticwebapp dbconnection create -n {name} -g {resource_group} -u {username} -p {password} -d {server_id} -b {db_name}",
                 checks=[JMESPathCheck("properties.region", location, case_sensitive=False),
                         JMESPathCheck("properties.resourceId", server_id)])

    @ResourceGroupPreparer(name_prefix='cli_test', location="westus")
    def test_staticwebapp_dbconnection_cosmosdb(self, resource_group):
        name = self.create_random_name("cli_test", length=20)
        server = self.create_random_name("cli-test", length=20)
        location = "West US"

        self.cmd(f"staticwebapp create -n {name} -g {resource_group} -l centralus")
        server_id = self.cmd(f"cosmosdb create -n {server} -g {resource_group}").get_output_in_json()["id"]

        self.cmd(f"staticwebapp dbconnection create -n {name} -g {resource_group} -d {server_id}",
                 checks=[JMESPathCheck("properties.region", location, case_sensitive=False),
                         JMESPathCheck("properties.resourceId", server_id)])

    def _get_mock_cmd(self):
        from azure.cli.core.mock import DummyCli
        from azure.cli.core import AzCommandsLoader
        from azure.cli.core.commands import AzCliCommand
        from azext_staticwebapp import StaticwebappCommandsLoader
        cli_ctx = DummyCli()

        loader = StaticwebappCommandsLoader(cli_ctx)
        cmd = AzCliCommand(loader, 'test', None)
        cmd.cli_ctx = cli_ctx
        return cmd

    @ResourceGroupPreparer(name_prefix='cli_test')
    def test_staticwebapp_dbconnection_mysql_flex(self, resource_group):
        name = self.create_random_name("cli_test", length=20)
        server = self.create_random_name("cli-test", length=20)
        username = "aturing"
        password = "thisisapassword123!"
        location = "East US"
        db_name = "tables"

        self.cmd(f"staticwebapp create -n {name} -g {resource_group}")
        # Creating flexible servers takes too long and the polling messes with test recordings
        server_id = f"/subscriptions/{self.get_subscription_id()}/resourceGroups/{resource_group}/providers/Microsoft.DBforMySQL/flexibleServers/{server}"

        mock_get_location = lambda *args, **kwargs: location
        handler = MySqlFlexHandler()
        handler.get_location = mock_get_location

        with mock.patch('azext_staticwebapp.custom.get_database_type', return_value=handler):
            conn = create_dbconnection(self._get_mock_cmd(), resource_group, name, server_id, db_name, username=username, password=password, environment="default")
            self.assertEqual(conn["properties"]["region"], location)
            self.assertEqual(conn["properties"]["resourceId"], server_id)

    @ResourceGroupPreparer(name_prefix='cli_test')
    def test_staticwebapp_dbconnection_pgsql_single(self, resource_group):
        name = self.create_random_name("cli_test", length=20)
        server = self.create_random_name("cli-test", length=20)
        username = "aturing"
        password = "thisisapassword123!"
        location = "West US"
        db_name = "tables"

        self.cmd(f"staticwebapp create -n {name} -g {resource_group}")
        server_id = self.cmd(f"postgres server create -l '{location}' -g {resource_group} -n {server} -u {username} -p {password}").get_output_in_json()["id"]
        self.cmd(f"postgres db create -g {resource_group} -n {db_name} -s {server}")

        self.cmd(f"staticwebapp dbconnection create -n {name} -g {resource_group} -u {username} -p {password} -d {server_id} -b {db_name}",
                 checks=[JMESPathCheck("properties.region", location, case_sensitive=False),
                         JMESPathCheck("properties.resourceId", server_id)])

    @ResourceGroupPreparer(name_prefix='cli_test')
    def test_staticwebapp_dbconnection_pgsql_flex(self, resource_group):
        name = self.create_random_name("cli_test", length=20)
        server = self.create_random_name("cli-test", length=20)
        username = "aturing"
        password = "thisisapassword123!"
        location = "East US"
        db_name = "tables"

        self.cmd(f"staticwebapp create -n {name} -g {resource_group}")
        # Creating flexible servers takes too long and the polling messes with test recordings
        server_id = f"/subscriptions/{self.get_subscription_id()}/resourceGroups/{resource_group}/providers/Microsoft.DBforMySQL/flexibleServers/{server}"

        mock_get_location = lambda *args, **kwargs: location
        handler = PgSqlFlexHandler()
        handler.get_location = mock_get_location

        with mock.patch('azext_staticwebapp.custom.get_database_type', return_value=handler):
            conn = create_dbconnection(self._get_mock_cmd(), resource_group, name, server_id, db_name, username=username, password=password, environment="default")
            self.assertEqual(conn["properties"]["region"], location)
            self.assertEqual(conn["properties"]["resourceId"], server_id)
