# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.command_modules.serviceconnector._resource_config import (
    RESOURCE,
    SOURCE_RESOURCES,
    TARGET_RESOURCES
)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))
resource_group = 'servicelinker-cli-test-group'

@unittest.skip('Need environment prepared')
class Serviceconnector_passwordlessScenarioTest(ScenarioTest):

    def test_aad_webapp_sql(self):
        self.kwargs.update({
            'subscription': get_subscription_id(self.cli_ctx),
            'source_resource_group': 'zxf-test',
            'target_resource_group': 'zxf-test',
            'site': 'xf-mi-test',
            'server': 'servicelinker-sql-mi',
            'database': 'clitest'
        })
        name = 'testconn'
        source_id = SOURCE_RESOURCES.get(RESOURCE.WebApp).format(**self.kwargs)
        target_id = TARGET_RESOURCES.get(RESOURCE.Sql).format(**self.kwargs)
        connection_id = source_id + "/providers/Microsoft.ServiceLinker/linkers/" + name

        # prepare
        self.cmd('webapp identity remove --ids {}'.format(source_id))
        self.cmd('sql server update -e false --ids {}'.format(target_id))
        self.cmd('sql db create -g {target_resource_group} -s {server} -n {database}')

        # create
        self.cmd('webapp connection create sql --connection {} --source-id {} --target-id {} '
                 '--system-identity --client-type dotnet'.format(name, source_id, target_id))
        # clean
        self.cmd('webapp connection delete --id {} --yes'.format(connection_id))

        # recreate and test
        self.cmd('webapp connection create sql --connection {} --source-id {} --target-id {} '
                 '--system-identity --client-type dotnet'.format(name, source_id, target_id))
        # clean
        self.cmd('webapp connection delete --id {} --yes'.format(connection_id))
        self.cmd('sql db delete -y -g {target_resource_group} -s {server} -n {database}')


    def test_aad_spring_mysqlflexible(self):
        self.kwargs.update({
            'subscription': get_subscription_id(self.cli_ctx),
            'source_resource_group': 'servicelinker-test-linux-group',
            'target_resource_group': 'zxf-test',
            'spring': 'springeuap',
            'app': 'mysqlflexmi',
            'deployment': 'default',
            'server': 'xf-mysqlflex-test',
            'database': 'mysqlDB',
        })
        mysql_identity_id = '/subscriptions/d82d7763-8e12-4f39-a7b6-496a983ec2f4/resourcegroups/zxf-test/providers/Microsoft.ManagedIdentity/userAssignedIdentities/servicelinker-aad-umi'

        # prepare params
        name = 'testconn'
        source_id = SOURCE_RESOURCES.get(RESOURCE.SpringCloud).format(**self.kwargs)
        target_id = TARGET_RESOURCES.get(RESOURCE.MysqlFlexible).format(**self.kwargs)
        connection_id = source_id + "/providers/Microsoft.ServiceLinker/linkers/" + name

        # prepare
        self.cmd('spring app identity remove -n {app} -s {spring} -g {source_resource_group} --system-assigned')
        self.cmd('mysql flexible-server ad-admin delete -g {target_resource_group} -s {server} -y')
        self.cmd('mysql flexible-server db create -g {target_resource_group} --server-name {server} --database-name {database}')
        # self.cmd('mysql flexible-server identity remove -g {target_resource_group} -s {server} -y --identity ' + mysql_identity_id)

        # create connection
        self.cmd('spring connection create mysql-flexible --connection {} --source-id {} --target-id {} '
                 '--client-type springboot --system-identity mysql-identity-id={}'.format(name, source_id, target_id, mysql_identity_id))
        # delete connection
        self.cmd('spring connection delete --id {} --yes'.format(connection_id))


        # create connection
        self.cmd('spring connection create mysql-flexible --connection {} --source-id {} --target-id {} '
                 '--client-type springboot --system-identity mysql-identity-id={}'.format(name, source_id, target_id, mysql_identity_id))
        # delete connection
        self.cmd('spring connection delete --id {} --yes'.format(connection_id))
        self.cmd('mysql flexible-server db delete -y -g {target_resource_group} --server-name {server} --database-name {database}')


    def test_aad_containerapp_postgresflexible(self):
        default_container_name = 'simple-hello-world-container'
        self.kwargs.update({
            'subscription': get_subscription_id(self.cli_ctx),
            'source_resource_group': 'zxf-test',
            'target_resource_group': 'zxf-test',
            'app': 'servicelinker-mysql-aca',
            'server': 'xf-pgflex-clitest',
            'database': 'testdb1',
            'containerapp_env': '/subscriptions/d82d7763-8e12-4f39-a7b6-496a983ec2f4/resourceGroups/container-app/providers/Microsoft.App/managedEnvironments/north-europe'
        })

        # prepare params
        name = 'testconn'
        source_id = SOURCE_RESOURCES.get(RESOURCE.ContainerApp).format(**self.kwargs)
        target_id = TARGET_RESOURCES.get(RESOURCE.PostgresFlexible).format(**self.kwargs)
        connection_id = source_id + "/providers/Microsoft.ServiceLinker/linkers/" + name

        # prepare
        self.cmd('containerapp delete -n {app} -g {source_resource_group}')
        self.cmd('containerapp create -n {app} -g {source_resource_group} --environment {containerapp_env} --image nginx')
        self.cmd('postgres flexible-server delete -y -g {target_resource_group} -n {server}')
        self.cmd('postgres flexible-server create -y -g {target_resource_group} -n {server}')
        self.cmd('postgres flexible-server db create -g {target_resource_group} -s {server} -d {database}')

        # create
        self.cmd('containerapp connection create postgres-flexible --connection {} --source-id {} --target-id {} '
                 '--system-identity --client-type springboot -c {}'.format(name, source_id, target_id, default_container_name))
        configs = self.cmd('containerapp connection list-configuration --id {}'.format(connection_id)).get_output_in_json();
        # clean
        self.cmd('containerapp connection delete --id {} --yes'.format(connection_id))
        #
        # # recreate and test
        # self.cmd('containerapp connection create postgres-flexible --connection {} --source-id {} --target-id {} '
        #          '--system-identity --client-type dotnet -c {}'.format(name, source_id, target_id, default_container_name))
        # clean
        # self.cmd('containerapp connection delete --id {} --yes'.format(connection_id))
        # self.cmd('postgres flexible-server delete -y -g {target_resource_group} -n {server}')


    def test_aad_webapp_postgressingle(self):
        self.kwargs.update({
            'subscription': "d82d7763-8e12-4f39-a7b6-496a983ec2f4",
            'source_resource_group': 'zxf-test',
            'target_resource_group': 'zxf-test',
            'site': 'xf-pg-app',
            'server': 'xfpostgre',
            'database': 'testdb'
        })

        # prepare params
        name = 'testconn'
        source_id = SOURCE_RESOURCES.get(RESOURCE.WebApp).format(**self.kwargs)
        target_id = TARGET_RESOURCES.get(RESOURCE.PostgresFlexible).format(**self.kwargs)
        connection_id = source_id + "/providers/Microsoft.ServiceLinker/linkers/" + name

        # prepare
        self.cmd('webapp identity remove --ids {}'.format(source_id))
        # self.cmd('postgres server delete -y -g {target_resource_group} -n {server}')
        # self.cmd('postgres server create -y -g {target_resource_group} -n {server}')
        self.cmd('postgres db delete -g {target_resource_group} -s {server} -n {database}')
        self.cmd('postgres db create -g {target_resource_group} -s {server} -n {database}')

        # create
        self.cmd('webapp connection create postgres-flexible --connection {} --source-id {} --target-id {} '
                 '--system-identity --client-type springboot'.format(name, source_id, target_id))
        configs = self.cmd('webapp connection list-configuration --id {}'.format(connection_id)).get_output_in_json();


    def test_local_postgresflexible_passwordless(self):
        self.kwargs.update({
            'subscription': get_subscription_id(self.cli_ctx),
            'target_resource_group': 'servicelinker-test-linux-group',
            'server': 'servicelinker-flexiblepostgresql',
            'database': 'test'
        })

        # prepare params
        name = 'testpostgresflex'
        target_id = TARGET_RESOURCES.get(
            RESOURCE.PostgresFlexible).format(**self.kwargs)

        # create connection
        self.cmd('connection create postgres-flexible -g {} --connection {} --target-id {} '
                 '--user-account --client-type springboot'.format(resource_group, name, target_id))

        # list connection
        self.cmd('connection list -g {}'.format(resource_group))

        # show connection
        connection = self.cmd(
            'connection show -g {} --connection {}'.format(
                resource_group, name),
            checks=[
                self.check('authInfo.authType', 'userAccount'),
                self.check('clientType', 'springBoot'),
                self.check('length(configurations)', 2),
            ]
        ).get_output_in_json()
        connection_id = connection.get('id')

        # update connection
        self.cmd('connection update postgres-flexible --id {} --client-type dotnet'.format(connection_id),
                 checks=[
            self.check('clientType', 'dotnet'),
            self.check('length(configurations)', 1),
        ]
        )

        # generate configuration
        self.cmd('connection generate-configuration --id {}'.format(connection_id))

        # validate connection
        self.cmd('connection validate --id {}'.format(connection_id))

        # show connection
        self.cmd('connection show --id {}'.format(connection_id))

        # delete connection
        self.cmd('connection delete --id {} --yes'.format(connection_id))


    def test_local_mysqlflexible_passwordless(self):
        self.kwargs.update({
            'subscription': get_subscription_id(self.cli_ctx),
            'target_resource_group': 'servicelinker-test-linux-group',
            'server': 'servicelinker-flexible-mysql',
            'database': 'mysqlDB'
        })

        # prepare params
        name = 'testconnmysqlflex'
        target_id = TARGET_RESOURCES.get(
            RESOURCE.MysqlFlexible).format(**self.kwargs)
        umi = '/subscriptions/d82d7763-8e12-4f39-a7b6-496a983ec2f4/resourcegroups/zxf-test/providers/Microsoft.ManagedIdentity/userAssignedIdentities/servicelinker-aad-umi'
        # create connection
        self.cmd('connection create mysql-flexible -g {} --connection {} --target-id {} '
                 '--user-account mysql-identity-id={} --client-type springboot'.format(resource_group, name, target_id, umi))

        # list connection
        self.cmd('connection list -g {}'.format(resource_group))

        # show connection
        connection = self.cmd(
            'connection show -g {} --connection {}'.format(
                resource_group, name),
            checks=[
                self.check('authInfo.authType', 'userAccount'),
                self.check('clientType', 'springBoot'),
                self.check('length(configurations)', 2),
            ]
        ).get_output_in_json()
        connection_id = connection.get('id')

        # update connection
        self.cmd('connection update mysql-flexible --id {} --client-type dotnet'.format(
            connection_id),
            checks=[self.check('clientType', 'dotnet')])

        # generate configuration
        self.cmd('connection generate-configuration --id {}'.format(connection_id))

        # validate connection
        self.cmd('connection validate --id {}'.format(connection_id))

        # show connection
        self.cmd('connection show --id {}'.format(connection_id))

        # delete connection
        self.cmd('connection delete --id {} --yes'.format(connection_id))


    def test_local_postgres_passwordless(self):
        self.kwargs.update({
            'subscription': get_subscription_id(self.cli_ctx),
            'target_resource_group': 'servicelinker-test-linux-group',
            'server': 'servicelinker-postgresql',
            'database': 'test'
        })

        # prepare params
        name = 'testconn17'
        target_id = TARGET_RESOURCES.get(
            RESOURCE.Postgres).format(**self.kwargs)

        # create connection
        self.cmd('connection create postgres -g {} --connection {} --target-id {} '
                 '--user-account --client-type springboot'.format(resource_group, name, target_id))

        # list connection
        self.cmd('connection list -g {}'.format(resource_group))

        # show connection
        connection = self.cmd(
            'connection show -g {} --connection {}'.format(
                resource_group, name),
            checks=[
                self.check('authInfo.authType', 'userAccount'),
                self.check('clientType', 'springBoot'),
                self.check('length(configurations)', 2),
            ]
        ).get_output_in_json()
        connection_id = connection.get('id')

        # update connection
        self.cmd('connection update postgres --id {} --client-type dotnet'.format(
            connection_id),
            checks=[self.check('clientType', 'dotnet')])

        # generate configuration
        self.cmd('connection generate-configuration --id {}'.format(connection_id))

        # validate connection
        self.cmd('connection validate --id {}'.format(connection_id))

        # show connection
        self.cmd('connection show --id {}'.format(connection_id))

        # delete connection
        self.cmd('connection delete --id {} --yes'.format(connection_id))


    def test_local_sql_passwordless(self):
        self.kwargs.update({
            'subscription': get_subscription_id(self.cli_ctx),
            'target_resource_group': 'servicelinker-test-linux-group',
            'server': 'servicelinker-sql',
            'database': 'handler-test'
        })

        # prepare params
        name = 'testconnsql'
        target_id = TARGET_RESOURCES.get(RESOURCE.Sql).format(**self.kwargs)

        # create connection
        self.cmd('connection create sql -g {} --connection {} --target-id {} '
                 '--user-account --client-type springboot'.format(resource_group, name, target_id, user, password))

        # list connection
        self.cmd('connection list -g {}'.format(resource_group))

        # show connection
        connection = self.cmd(
            'connection show -g {} --connection {}'.format(
                resource_group, name),
            checks=[
                self.check('authInfo.authType', 'userAccount'),
                self.check('clientType', 'springBoot'),
                self.check('length(configurations)', 2),
            ]
        ).get_output_in_json()
        connection_id = connection.get('id')

        # update connection
        self.cmd('connection update sql --id {} --client-type dotnet'.format(
            connection_id),
            checks=[self.check('clientType', 'dotnet')])

        # generate configuration
        self.cmd('connection generate-configuration --id {}'.format(connection_id))

        # validate connection
        self.cmd('connection validate --id {}'.format(connection_id))

        # show connection
        self.cmd('connection show --id {}'.format(connection_id))

        # delete connection
        self.cmd('connection delete --id {} --yes'.format(connection_id))
