# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)

class Cosmosdb_previewcassandraRbacScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_cassandra_role', location='westus2')
    def test_cosmosdb_cassandra_role(self, resource_group):
        acc_name = self.create_random_name(prefix='cli', length=15)
        db_name = self.create_random_name(prefix='cli', length=15)

        subscription = self.get_subscription_id()
        
        role_def_name1 = 'efc54be2-2c55-4041-8090-05f55f6e4601'
        role_def_name2 = 'efc54be2-2c55-4041-8090-05f55f6e4602'
        
        role_def_id1 = 'efc54be2-2c55-4041-8090-05f55f6e4601'
        role_def_id2 = 'efc54be2-2c55-4041-8090-05f55f6e4602'
        
        user_definition_id = db_name + '.testUser'
        user_name = 'testUser'
        test_name = 'testUser'
        test_name2 = 'testUser2'
        
        scope = ('/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.DocumentDB/databaseAccounts/{2}').format(subscription, resource_group, acc_name)
        
        role_definition_create_body = (' {{ \\"Id\\": \\"{0}\\",\\"RoleName\\": \\"{1}\\",\\"type\\": \\"CustomRole\\",\\"description\\": \\"Custom role to read Cosmos DB metadata\\",\\"AssignableScopes\\":[\\"{2}\\"],\\"Permissions\\": [{{\\"dataActions\\": [\\"Microsoft.DocumentDB/databaseAccounts/readMetadata\\"]}}]  }} ').format(
            role_def_name1, test_name, scope)   
            
        role_definition_update_body = (' {{ \\"Id\\": \\"{0}\\",\\"RoleName\\": \\"{1}\\",\\"type\\": \\"CustomRole\\",\\"description\\": \\"Custom UPDATED role to read Cosmos DB metadata\\",\\"AssignableScopes\\":[\\"{2}\\"],\\"Permissions\\": [{{\\"dataActions\\": [\\"Microsoft.DocumentDB/databaseAccounts/readMetadata\\"]}}]  }} ').format(
            role_def_name1, test_name, scope) 
            
        role_definition_create_body2 = (' {{ \\"Id\\": \\"{0}\\",\\"RoleName\\": \\"{1}\\",\\"type\\": \\"CustomRole\\",\\"description\\": \\"Custom SECOND role to read Cosmos DB metadata\\",\\"AssignableScopes\\":[\\"{2}\\"],\\"Permissions\\": [{{\\"dataActions\\": [\\"Microsoft.DocumentDB/databaseAccounts/readMetadata\\"]}}]  }} ').format(
            role_def_name2, test_name2, scope) 
            
        fully_qualified_role_def_id1 = '/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.DocumentDB/databaseAccounts/{2}/cassandraRoleDefinitions/{3}'.format(
            subscription, resource_group, acc_name, role_def_id1)
        fully_qualified_role_def_id2 = '/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.DocumentDB/databaseAccounts/{2}/cassandraRoleDefinitions/{3}'.format(
            subscription, resource_group, acc_name, role_def_id2)
            
        # Contract violation request body
        empty_id_role_definition_create_body =  (' {{ \\"RoleName\\": \\"{1}\\",\\"type\\": \\"CustomRole\\",\\"description\\": \\"Custom role to read Cosmos DB metadata\\",\\"AssignableScopes\\":[\\"{2}\\"],\\"Permissions\\": [{{\\"dataActions\\": [\\"Microsoft.DocumentDB/databaseAccounts/readMetadata\\"]}}]  }} ').format(
            role_def_name1, test_name, scope)  
        invalid_role_id_role_definition_create_body = (' {{ \\"Id\\": \\"randomid\\",\\"RoleName\\": \\"{1}\\",\\"type\\": \\"CustomRole\\",\\"description\\": \\"Custom role to read Cosmos DB metadata\\",\\"AssignableScopes\\":[\\"{2}\\"],\\"Permissions\\": [{{\\"dataActions\\": [\\"Microsoft.DocumentDB/databaseAccounts/readMetadata\\"]}}]  }} ').format(
            role_def_name1, test_name, scope)  
        empty_name_role_definition_create_body = (' {{ \\"Id\\": \\"{0}\\",\\"RoleName\\": \\"\\",\\"type\\": \\"CustomRole\\",\\"description\\": \\"Custom role to read Cosmos DB metadata\\",\\"AssignableScopes\\":[\\"{2}\\"],\\"Permissions\\": [{{\\"dataActions\\": [\\"Microsoft.DocumentDB/databaseAccounts/readMetadata\\"]}}]  }} ').format(
            role_def_name1, test_name, scope)  

        no_resource_role_definition_create_body = (' {{ \\"RoleName\\": \\"{1}\\",\\"type\\": \\"CustomRole\\",\\"description\\": \\"Custom role to read Cosmos DB metadata\\",\\"Permissions\\": [{{\\"dataActions\\": [\\"Microsoft.DocumentDB/databaseAccounts/readMetadata\\"]}}]  }} ').format(
            role_def_name1, test_name, scope)  
        no_actions_role_definition_create_body = (' {{ \\"RoleName\\": \\"{1}\\",\\"type\\": \\"CustomRole\\",\\"description\\": \\"Custom role to read Cosmos DB metadata\\",\\"AssignableScopes\\":[\\"{2}\\"] }} ').format(
            role_def_name1, test_name, scope)  

        self.kwargs.update({
            'acc': acc_name,
            'db_name': db_name,
            'create_body': role_definition_create_body,
            'update_body': role_definition_update_body,
            'create_body2': role_definition_create_body2,
            
            'role_def_id1': role_def_id1,
            'fully_qualified_role_def_id1': fully_qualified_role_def_id1,
            'role_def_id2': role_def_id2,
            'user_name': user_name,
            'role_def_name1': role_def_name1,
            'role_def_name2': role_def_name2,
            'fully_qualified_role_def_id2': fully_qualified_role_def_id2,
            
            'empty_role_def_id_body': empty_id_role_definition_create_body,
            'inalid_id_role_def_create_body': invalid_role_id_role_definition_create_body,
            'empty_role_name_create_body': empty_name_role_definition_create_body,
            'no_resource_role_def_body': no_resource_role_definition_create_body,
            'no_actions_role_def_body': no_actions_role_definition_create_body,
            
            'test_role_name': test_name,

        })


        self.cmd(
            'az cosmosdb create -n {acc} -g {rg} --kind GlobalDocumentDB --capabilities EnableCassandra')
            
        self.cmd(
            'az cosmosdb show --name {acc} --resource-group {rg}')        
        
        self.cmd(
            'az cosmosdb cassandra keyspace create -g {rg} -a {acc} -n {db_name}')

        # Contract Violation for Role Definition. Failure tests
        self.cmd('az cosmosdb cassandra role definition create -g {rg} -a {acc} -b "{empty_role_def_id_body}"', expect_failure=True)
        self.cmd('az cosmosdb cassandra role definition create -g {rg} -a {acc} -b "{inalid_id_role_def_create_body}"', expect_failure=True)
        self.cmd('az cosmosdb cassandra role definition create -g {rg} -a {acc} -b "{empty_role_name_create_body}"', expect_failure=True)
        self.cmd('az cosmosdb cassandra role definition create -g {rg} -a {acc} -b "{no_resource_role_def_body}"', expect_failure=True)
        self.cmd('az cosmosdb cassandra role definition create -g {rg} -a {acc} -b "{no_actions_role_def_body}"', expect_failure=True)
                
        # Make sure same role def does not exist
        self.cmd(
            'az cosmosdb cassandra role definition delete -g {rg} -a {acc} --role-definition-id {role_def_id1} --yes')
        role_definition_list = self.cmd(
            'az cosmosdb cassandra role definition list -g {rg} -a {acc}').get_output_in_json()
        assert len(role_definition_list) == 2 # 2 built in roles
            
        assert self.cmd(
            'az cosmosdb cassandra role definition exists -g {rg} -a {acc} --role-definition-id 00000000-0000-0000-0000-000000000001').get_output_in_json()
            
        # Success Tests
        self.cmd('az cosmosdb cassandra role definition create -g {rg} -a {acc} -b "{create_body}"', checks=[
            self.check('id', fully_qualified_role_def_id1),
            self.check('roleName', user_name)
        ])
        
        self.cmd('az cosmosdb cassandra role definition show -g {rg} -a {acc} --role-definition-id {role_def_id1}', checks=[
            self.check('roleName', user_name)
        ])

        self.cmd('az cosmosdb cassandra role definition update -g {rg} -a {acc} -b "{update_body}"', checks=[
            self.check('id', fully_qualified_role_def_id1),
            self.check('length(permissions[0].dataActions)', 1),
            self.check('permissions[0].dataActions[0]', 'Microsoft.DocumentDB/databaseAccounts/readMetadata')
        ])

        # Make sure same role def does not exist
        self.cmd(
            'az cosmosdb cassandra role definition delete -g {rg} -a {acc} --role-definition-id {role_def_id2} --yes')
        role_definition_list = self.cmd(
            'az cosmosdb cassandra role definition list -g {rg} -a {acc}').get_output_in_json()
        assert len(role_definition_list) == 3
        
        self.cmd('az cosmosdb cassandra role definition create -g {rg} -a {acc} -b "{create_body2}"', checks=[
            self.check('id', fully_qualified_role_def_id2),
            self.check('roleName', 'testUser2'),
        ])

        role_definition_list = self.cmd(
            'az cosmosdb cassandra role definition list -g {rg} -a {acc}').get_output_in_json()
        assert len(role_definition_list) == 4
        
        self.cmd(
            'az cosmosdb cassandra role definition delete -g {rg} -a {acc} --role-definition-id {role_def_id1} --yes')
        role_definition_list = self.cmd(
            'az cosmosdb cassandra role definition list -g {rg} -a {acc}').get_output_in_json()
        assert len(role_definition_list) == 3

        self.cmd(
            'az cosmosdb cassandra role definition delete -g {rg} -a {acc} --role-definition-id {role_def_id2} --yes')
        role_definition_list = self.cmd(
            'az cosmosdb cassandra role definition list -g {rg} -a {acc}').get_output_in_json()
        assert len(role_definition_list) == 2
