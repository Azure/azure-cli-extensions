# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (
    JMESPathCheck,
    NoneCheck,
    ResourceGroupPreparer,
    ScenarioTest,
    LocalContextScenarioTest,
    live_only)

SERVER_NAME_PREFIX = 'azuredbclitest-'
SERVER_NAME_MAX_LENGTH = 20
SERVER_LOGIN_PWD_PREFIX = 'cliPwd'
SERVER_LOGIN_PWD_MAX_LENGTH = 15


class RdbmsConnectMgmtScenarioTest(ScenarioTest):

    postgres_location = 'eastus'
    mysql_location = 'northeurope'

    @AllowLargeResponse()
    @ResourceGroupPreparer(location=postgres_location)
    @live_only()
    def test_postgres_flexible_server_connect(self, resource_group):
        self._test_successful_connect('postgres', resource_group)
        # self._test_vnet_connect('postgres', resource_group)

    @AllowLargeResponse()
    @ResourceGroupPreparer(location=mysql_location)
    @live_only()
    def test_mysql_flexible_server_connect(self, resource_group):
        self._test_successful_connect('mysql', resource_group)
        # self._test_vnet_connect('mysql', resource_group)

    def _test_successful_connect(self, database_engine, resource_group):
        # setup variables for commands
        server_name = self.create_random_name(SERVER_NAME_PREFIX, SERVER_NAME_MAX_LENGTH)
        username = 'cliuser'
        storage_size = 32
        public_access = 'none'
        simple_query = '"select 1;"'
        if database_engine == 'postgres':
            version = '12'
            location = self.postgres_location
            default_database = 'postgres'
        elif database_engine == 'mysql':
            version = '5.7'
            location = self.mysql_location
            default_database = 'flexibleserverdb'

        # create server with public access enabled for all IPs
        self.cmd('{} flexible-server create -g {} -n {} -l {} --admin-user {} --storage-size {} --version {} --public-access {}'.
                 format(database_engine, resource_group, server_name, location, username, storage_size, version, public_access))

        # update password for generated username and server with a generated password
        generated_password = self.create_random_name(SERVER_LOGIN_PWD_PREFIX, SERVER_LOGIN_PWD_MAX_LENGTH)
        self.cmd('{} flexible-server update -g {} -n {} -p {}'.format(database_engine, resource_group, server_name, generated_password))

        # test connect without firewall
        self.cmd('{} flexible-server connect -n {} -u {} -p {}'.
                 format(database_engine, server_name, username, generated_password),
                 expect_failure=True)

        # add firewall
        firewall_rule_name = 'allIps'
        start_ip_address = '0.0.0.0'
        end_ip_address = '255.255.255.255'
        firewall_rule_checks = [JMESPathCheck('name', firewall_rule_name),
                                JMESPathCheck('endIpAddress', end_ip_address),
                                JMESPathCheck('startIpAddress', start_ip_address)]

        # firewall-rule create
        self.cmd('{} flexible-server firewall-rule create -g {} -n {} --rule-name {} '
                 '--start-ip-address {} --end-ip-address {}'
                 .format(database_engine, resource_group, server_name, firewall_rule_name, start_ip_address, end_ip_address),
                 checks=firewall_rule_checks)

        # test connection to the server without command/database specified
        self.cmd('{} flexible-server connect -n {} -u {} -p {}'.
                 format(database_engine, server_name, username, generated_password),
                 checks=NoneCheck())

        # test connection to the server with a simple query
        self.cmd('{} flexible-server execute -n {} -u {} -p {} -d {} -q {}'
                 .format(database_engine, server_name, username, generated_password, default_database, simple_query),
                 checks=[JMESPathCheck('length(@)', 1)])

        # test with invalid username
        username_wrong = 'fakeusername'
        self.cmd('{} flexible-server execute -n {} -u {} -p {} -d {} -q {}'
                 .format(database_engine, server_name, username_wrong, generated_password, default_database, simple_query),
                 expect_failure=True)

        # test file execution
        file_path = "./test.sql"
        with open(file_path, "w") as sql_file:
            sql_file.write("CREATE DATABASE sampledb;")

        self.cmd('{} flexible-server execute -n {} -u {} -p {} -d {} -f {}'
                 .format(database_engine, server_name, username, generated_password, default_database, file_path))

        # test file execution encoded with BOM
        with open(file_path, "wb") as sql_file:
            sql_file.write(b"\xef\xbb\xbfCREATE DATABASE sampledb2;")

        self.cmd('{} flexible-server execute -n {} -u {} -p {} -d {} -f {}'
                 .format(database_engine, server_name, username, generated_password, default_database, file_path))

        os.remove(file_path)

    def _test_vnet_connect(self, database_engine, resource_group):
        # setup variables for commands
        server_name = self.create_random_name(SERVER_NAME_PREFIX, SERVER_NAME_MAX_LENGTH)
        username = 'cliuser'
        storage_size = 32
        if database_engine == 'postgres':
            version = '12'
            location = self.postgres_location
        elif database_engine == 'mysql':
            version = '5.7'
            location = self.mysql_location

        # create server with vnet access
        self.cmd('{} flexible-server create -g {} -n {} -l {} --admin-user {} --storage-size {} --version {}'.
                 format(database_engine, resource_group, server_name, location, username, storage_size, version))

        # update password for generated username and server with a generated password
        generated_password = self.create_random_name(SERVER_LOGIN_PWD_PREFIX, SERVER_LOGIN_PWD_MAX_LENGTH)
        self.cmd('{} flexible-server update -g {} -n {} -p {}'.format(database_engine, resource_group, server_name, generated_password))

        # test connect with vnet and no firewall
        self.cmd('{} flexible-server connect -n {} -u {} -p {}'
                 .format(database_engine, server_name, username, generated_password), expect_failure=True)

        # add firewall
        firewall_rule_name = 'all_ips'
        start_ip_address = '0.0.0.0'
        end_ip_address = '255.255.255.255'
        firewall_rule_checks = [JMESPathCheck('name', firewall_rule_name),
                                JMESPathCheck('endIpAddress', end_ip_address),
                                JMESPathCheck('startIpAddress', start_ip_address)]

        # firewall-rule create
        self.cmd('{} flexible-server firewall-rule create -g {} -n {} --rule-name {} '
                 '--start-ip-address {} --end-ip-address {} '
                 .format(database_engine, resource_group, server_name, firewall_rule_name, start_ip_address, end_ip_address),
                 checks=firewall_rule_checks)

        # test connection to the server without command/database specified and with firewall, but vnet
        self.cmd('{} flexible-server connect -n {} -u {} -p {}'.
                 format(database_engine, server_name, username, generated_password),
                 expect_failure=True)
