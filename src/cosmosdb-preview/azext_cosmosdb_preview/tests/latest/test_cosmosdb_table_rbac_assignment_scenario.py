# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)

class Cosmosdb_previewtableRbacAssignmentScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_table_role_assignment', location='westus2')
    def test_cosmosdb_table_role_assignment(self):
        acc_name = self.create_random_name(prefix='cli', length=15)
        db_name = self.create_random_name(prefix='cli', length=15)

        role_assignment_id = 'cb8ed2d7-2371-4e3c-bd31-6cc1560e84f8'

        self.kwargs.update({
            'acc': acc_name,
            'db_name': db_name,
            'role_assignment_id': role_assignment_id,
        })

        #setup
        account = self.cmd(
            'az cosmosdb create --disable-local-auth true -n {acc} -g {rg} --kind GlobalDocumentDB --capabilities EnableTable --assign-identity [system]').get_output_in_json()
        scope = account['id']
        principal_id = account['identity']['principalId']
        assert principal_id
        builtin_role_def_id_full = scope + '/tableRoleDefinitions/00000000-0000-0000-0000-000000000001'
        builtin_role_def_id_full_update = scope + '/tableRoleDefinitions/00000000-0000-0000-0000-000000000002'
        self.kwargs.update({
            'scope': scope,
            'principal_id': principal_id,
            'builtin_role_def_id_full': builtin_role_def_id_full,
            'builtin_role_def_id_full_update': builtin_role_def_id_full_update,
        })
        self.cmd(
            'az cosmosdb show --name {acc} --resource-group {rg}')
        self.cmd(
            'az cosmosdb table create -g {rg} -a {acc} -n {db_name}')

        # ensure the built-in role exists
        assert self.cmd(
            'az cosmosdb table role definition exists -g {rg} -a {acc} --role-definition-id 00000000-0000-0000-0000-000000000001').get_output_in_json()
        assert self.cmd(
            'az cosmosdb table role definition exists -g {rg} -a {acc} --role-definition-id 00000000-0000-0000-0000-000000000002').get_output_in_json()
        
        # ensure test role assignment doesnt already exists     
        self.cmd(
            'az cosmosdb table role assignment delete -g {rg} -a {acc} --role-assignment-id cb8ed2d7-2371-4e3c-bd31-6cc1560e84f8 --yes')
        role_assignment_list = self.cmd(
            'az cosmosdb table role assignment list -g {rg} -a {acc}').get_output_in_json()
        assert len(role_assignment_list) == 0
        
        # Create a role assignment 
        self.cmd('az cosmosdb table role assignment create -g {rg} -a {acc} --scope {scope} --principal-id {principal_id} --role-definition-id {builtin_role_def_id_full} --role-assignment-id {role_assignment_id}', checks=[
            self.check('scope', scope),
            self.check('principalId', principal_id),
            self.check('roleDefinitionId', builtin_role_def_id_full)
        ])
        
        # Show/list role assignment
        self.cmd('az cosmosdb table role assignment show -g {rg} -a {acc} --role-assignment-id cb8ed2d7-2371-4e3c-bd31-6cc1560e84f8', checks=[
            self.check('name', 'cb8ed2d7-2371-4e3c-bd31-6cc1560e84f8')
        ])
        
        role_assignment_list = self.cmd(
            'az cosmosdb table role assignment list -g {rg} -a {acc}').get_output_in_json()
        assert len(role_assignment_list) == 1
        
        # Update role assignment
        self.cmd('az cosmosdb table role assignment update -g {rg} -a {acc} --scope {scope} --principal-id {principal_id} --role-definition-id {builtin_role_def_id_full_update} --role-assignment-id {role_assignment_id}', checks=[
            self.check('scope', scope),
            self.check('principalId', principal_id),
            self.check('roleDefinitionId', builtin_role_def_id_full_update)
        ])
        
        # Delete role assignment, for cleanup
        # ensure role assignment does not exist
        self.cmd(
            'az cosmosdb table role assignment delete -g {rg} -a {acc} --role-assignment-id cb8ed2d7-2371-4e3c-bd31-6cc1560e84f8 --yes')
        role_assignment_list = self.cmd(
            'az cosmosdb table role assignment list -g {rg} -a {acc}').get_output_in_json()
        assert len(role_assignment_list) == 0
