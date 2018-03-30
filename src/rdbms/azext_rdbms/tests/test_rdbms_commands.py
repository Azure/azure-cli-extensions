# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk.base import execute
from azure.cli.testsdk.exceptions import CliTestError   # pylint: disable=unused-import
from azure.cli.testsdk import (
    JMESPathCheck,
    NoneCheck,
    ResourceGroupPreparer,
    ScenarioTest)
from azure.cli.testsdk.preparers import (
    AbstractPreparer,
    SingleValueReplacer)


# Constants
SERVER_NAME_PREFIX = 'azuredbclitest'
SERVER_NAME_MAX_LENGTH = 63


class ServerPreparer(AbstractPreparer, SingleValueReplacer):
    # pylint: disable=too-many-instance-attributes
    def __init__(self, engine_type='mysql', engine_parameter_name='database_engine',
                 name_prefix=SERVER_NAME_PREFIX, parameter_name='server', location='westus',
                 admin_user='cloudsa', admin_password='SecretPassword123',
                 resource_group_parameter_name='resource_group', skip_delete=True,
                 sku_name='GP_Gen5_2'):
        super(ServerPreparer, self).__init__(name_prefix, SERVER_NAME_MAX_LENGTH)
        from azure.cli.testsdk import TestCli
        self.cli_ctx = TestCli()
        self.engine_type = engine_type
        self.engine_parameter_name = engine_parameter_name
        self.location = location
        self.parameter_name = parameter_name
        self.admin_user = admin_user
        self.admin_password = admin_password
        self.resource_group_parameter_name = resource_group_parameter_name
        self.skip_delete = skip_delete
        self.sku_name = sku_name

    def create_resource(self, name, **kwargs):
        group = self._get_resource_group(**kwargs)
        template = 'az {} server create -l {} -g {} -n {} -u {} -p {} --sku-name {}'
        execute(self.cli_ctx, template.format(self.engine_type,
                                              self.location,
                                              group, name,
                                              self.admin_user,
                                              self.admin_password,
                                              self.sku_name))
        return {self.parameter_name: name,
                self.engine_parameter_name: self.engine_type}

    def remove_resource(self, name, **kwargs):
        if not self.skip_delete:
            group = self._get_resource_group(**kwargs)
            execute(self.cli_ctx, 'az {} server delete -g {} -n {} --yes'.format(self.engine_type, group, name))

    def _get_resource_group(self, **kwargs):
        return kwargs.get(self.resource_group_parameter_name)


class ServerMgmtScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(parameter_name='resource_group_1')
    def test_mysql_server_mgmt(self, resource_group_1):
        self._test_server_mgmt('mysql', resource_group_1)

    @ResourceGroupPreparer(parameter_name='resource_group_1')
    def test_postgres_server_mgmt(self, resource_group_1):
        self._test_server_mgmt('postgres', resource_group_1)

    def _test_server_mgmt(self, database_engine, resource_group_1):
        servers = [self.create_random_name(SERVER_NAME_PREFIX, SERVER_NAME_MAX_LENGTH),
                   self.create_random_name('azuredbclirestore', SERVER_NAME_MAX_LENGTH),
                   self.create_random_name('azuredbcligeorestore', SERVER_NAME_MAX_LENGTH)]
        admin_login = 'cloudsa'
        admin_passwords = ['SecretPassword123', 'SecretPassword456']
        edition = 'GeneralPurpose'
        old_cu = 2
        family = 'Gen5'
        skuname = '{}_{}_{}'.format("GP", family, old_cu)

        rg = resource_group_1
        loc = 'westus'

        # test create server
        self.cmd('{} server create -g {} --name {} -l {} '
                 '--admin-user {} --admin-password {} '
                 '--sku-name {} --tags key=1'
                 .format(database_engine, rg, servers[0], loc,
                         admin_login, admin_passwords[0], skuname),
                 checks=[
                     JMESPathCheck('name', servers[0]),
                     JMESPathCheck('resourceGroup', rg),
                     JMESPathCheck('administratorLogin', admin_login),
                     JMESPathCheck('sslEnforcement', 'Enabled'),
                     JMESPathCheck('tags.key', '1'),
                     JMESPathCheck('sku.capacity', old_cu),
                     JMESPathCheck('sku.tier', edition)])

        # test show server
        self.cmd('{} server show -g {} --name {}'
                 .format(database_engine, rg, servers[0]),
                 checks=[
                     JMESPathCheck('name', servers[0]),
                     JMESPathCheck('administratorLogin', admin_login),
                     JMESPathCheck('sku.capacity', old_cu),
                     JMESPathCheck('resourceGroup', rg)]).get_output_in_json()

        # test list servers
        self.cmd('{} server list -g {}'.format(database_engine, resource_group_1),
                 checks=[JMESPathCheck('type(@)', 'array')])

        # test list servers without resource group
        self.cmd('{} server list'.format(database_engine),
                 checks=[JMESPathCheck('type(@)', 'array')])

        # test delete server
        self.cmd('{} server delete -g {} --name {} --yes'
                 .format(database_engine, rg, servers[0]), checks=NoneCheck())

        # test list server should be 0
        self.cmd('{} server list -g {}'.format(database_engine, rg), checks=[NoneCheck()])
