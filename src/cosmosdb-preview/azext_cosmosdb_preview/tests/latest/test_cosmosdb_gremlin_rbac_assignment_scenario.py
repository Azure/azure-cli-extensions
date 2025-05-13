# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)

class Cosmosdb_previewgremlinRbacAssignmentScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_gremlin_role_assignment', location='westus2')
    def test_cosmosdb_gremlin_role_assignment(self, resource_group):
        acc_name = self.create_random_name(prefix='cli', length=15)
        db_name = self.create_random_name(prefix='cli', length=15)

        subscription = self.get_subscription_id()
        
        user_definition_id = db_name + '.testUser'
        user_name = 'testUser'
        
        role_def_id = 'be79875a-2cc4-40d5-8958-566017875b39'
        role_assignment_id = 'cb8ed2d7-2371-4e3c-bd31-6cc1560e84f8'
        principal_id = 'ca95ad70-0b97-48cd-a757-57662ffa33e9'
        
        scope = ('/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.DocumentDB/databaseAccounts/{2}').format(subscription, resource_group, acc_name)        
        
        builtin_role_def_id_full = '/subscriptions/80be3961-0521-4a0a-8570-5cd5a4e2f98c/resourceGroups/cli_test_cosmosdb_gremlin_role_assignmentu4ss2n535bbvhe2wmufck5yfhyziujp77gg4/providers/Microsoft.DocumentDB/databaseAccounts/clikznzrccyiwbv/gremlinRoleDefinitions/00000000-0000-0000-0000-000000000001'
        
        builtin_role_def_id_full_update = '/subscriptions/80be3961-0521-4a0a-8570-5cd5a4e2f98c/resourceGroups/cli_test_cosmosdb_gremlin_role_assignmentu4ss2n535bbvhe2wmufck5yfhyziujp77gg4/providers/Microsoft.DocumentDB/databaseAccounts/clikznzrccyiwbv/gremlinRoleDefinitions/00000000-0000-0000-0000-000000000002'
        
        self.kwargs.update({
            'acc': acc_name,
            'db_name': db_name,
            
            'user_name': user_name,
            
            'principal_id': principal_id,
            'scope': scope,
            'builtin_role_def_id_full': builtin_role_def_id_full,
            'role_assignment_id': role_assignment_id,
            'builtin_role_def_id_full_update': builtin_role_def_id_full_update
        })

        #setup
        self.cmd(
            'az cosmosdb create -n {acc} -g {rg} --kind GlobalDocumentDB --capabilities EnableGremlin')            
        self.cmd(
            'az cosmosdb show --name {acc} --resource-group {rg}')
        self.cmd(
            'az cosmosdb gremlin database create -g {rg} -a {acc} -n {db_name}')

        # ensure the built-in role exists
        assert self.cmd(
            'az cosmosdb gremlin role definition exists -g {rg} -a {acc} --role-definition-id 00000000-0000-0000-0000-000000000001').get_output_in_json()
        
        # ensure test role assignment doesnt already exists     
        self.cmd(
            'az cosmosdb gremlin role assignment delete -g {rg} -a {acc} --role-assignment-id cb8ed2d7-2371-4e3c-bd31-6cc1560e84f8 --yes')
        role_assignment_list = self.cmd(
            'az cosmosdb gremlin role assignment list -g {rg} -a {acc}').get_output_in_json()
        assert len(role_assignment_list) == 0
        
        # Create a role assignment 
        self.cmd('az cosmosdb gremlin role assignment create -g {rg} -a {acc} --scope {scope} --principal-id {principal_id} --role-definition-id {builtin_role_def_id_full} --role-assignment-id {role_assignment_id}', checks=[
            self.check('scope', scope),
            self.check('principalId', principal_id)
        ])
        
        # Show/list role assignment
        self.cmd('az cosmosdb gremlin role assignment show -g {rg} -a {acc} --role-assignment-id cb8ed2d7-2371-4e3c-bd31-6cc1560e84f8', checks=[
            self.check('name', 'cb8ed2d7-2371-4e3c-bd31-6cc1560e84f8')
        ])
        
        role_assignment_list = self.cmd(
            'az cosmosdb gremlin role assignment list -g {rg} -a {acc}').get_output_in_json()
        assert len(role_assignment_list) == 1
        
        # Update role assignment
        self.cmd('az cosmosdb gremlin role assignment update -g {rg} -a {acc} --scope {scope} --principal-id {principal_id} --role-definition-id {builtin_role_def_id_full_update} --role-assignment-id {role_assignment_id}', checks=[
            self.check('scope', scope),
            self.check('principalId', principal_id)
        ])
        
        # Delete role assignment, for cleanup
        # ensure role assignment does not exist
        self.cmd(
            'az cosmosdb gremlin role assignment delete -g {rg} -a {acc} --role-assignment-id cb8ed2d7-2371-4e3c-bd31-6cc1560e84f8 --yes')
        role_assignment_list = self.cmd(
            'az cosmosdb gremlin role assignment list -g {rg} -a {acc}').get_output_in_json()
        assert len(role_assignment_list) == 0
        