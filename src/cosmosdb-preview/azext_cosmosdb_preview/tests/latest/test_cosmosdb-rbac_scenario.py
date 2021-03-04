# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


class Cosmosdb_previewRbacScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_sql_role')
    def test_cosmosdb_sql_role(self, resource_group):
        acc_name = self.create_random_name(prefix='cli', length=15)
        db_name = self.create_random_name(prefix='cli', length=15)

        subscription = self.get_subscription_id()
        role_def_id = 'be79875a-2cc4-40d5-8958-566017875b39'
        role_def_id2 = '6328f5f7-dbf7-4244-bba8-fbb9d8066506'
        role_assignment_id = 'cb8ed2d7-2371-4e3c-bd31-6cc1560e84f8'
        role_assignment_id2 = '09d117e6-ab6a-4a8b-948a-c6c34aa631db'
        role_definition_create_body = ' {{ \\"Id\\": \\"{0}\\", \\"RoleName\\": \\"roleName\\", \\"Type\\": \\"CustomRole\\", \\"AssignableScopes\\": [ \\"/\\" ], \\"DataActions\\": [ \\"Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/items/create\\", \\"Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/items/read\\" ] }} '.format(role_def_id)
        role_definition_update_body = ' {{ \\"Id\\": \\"{0}\\", \\"RoleName\\": \\"roleName2\\", \\"Type\\": \\"CustomRole\\", \\"AssignableScopes\\": [ \\"/\\" ], \\"Permissions\\": [ {{ \\"DataActions\\": [ \\"Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/items/create\\" ] }}, {{ \\"DataActions\\": [ \\"Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/items/read\\" ] }} ] }}'.format(role_def_id)
        role_definition_create_body2 = ' {{ \\"Id\\": \\"{0}\\", \\"RoleName\\": \\"roleName3\\", \\"Type\\": \\"CustomRole\\", \\"AssignableScopes\\": [ \\"/\\" ], \\"Permissions\\": [ {{ \\"DataActions\\": [ \\"Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/items/create\\" ] }}, {{ \\"DataActions\\": [ \\"Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/items/read\\" ] }}, {{ \\"DataActions\\": [ \\"Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/items/replace\\" ] }} ] }}'.format(role_def_id2)
        fully_qualified_role_def_id = '/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.DocumentDB/databaseAccounts/{2}/sqlRoleDefinitions/{3}'.format(subscription, resource_group, acc_name, role_def_id)
        fully_qualified_role_def_id2 = '/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.DocumentDB/databaseAccounts/{2}/sqlRoleDefinitions/{3}'.format(subscription, resource_group, acc_name, role_def_id2)
        fully_qualified_role_assignment_id = '/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.DocumentDB/databaseAccounts/{2}/sqlRoleAssignments/{3}'.format(subscription, resource_group, acc_name, role_assignment_id)
        fully_qualified_role_assignment_id2 = '/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.DocumentDB/databaseAccounts/{2}/sqlRoleAssignments/{3}'.format(subscription, resource_group, acc_name, role_assignment_id2)
        assignable_scope = '/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.DocumentDB/databaseAccounts/{2}'.format(subscription, resource_group, acc_name)
        scope = '/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.DocumentDB/databaseAccounts/{2}/dbs/{3}'.format(subscription, resource_group, acc_name, db_name)
        principal_id = 'ed4c2395-a18c-4018-afb3-6e521e7534d2'

        self.kwargs.update({
            'acc': acc_name,
            'db_name': db_name,
            'create_body': role_definition_create_body,
            'update_body': role_definition_update_body,
            'create_body2': role_definition_create_body2,
            'role_def_id': role_def_id,
            'fully_qualified_role_def_id': fully_qualified_role_def_id,
            'role_def_id2': role_def_id2,
            'fully_qualified_role_def_id2': fully_qualified_role_def_id2,
            'role_assignment_id': role_assignment_id,
            'role_assignment_id2': role_assignment_id2,
            'fully_qualified_role_assignment_id': fully_qualified_role_assignment_id,
            'fully_qualified_role_assignment_id2': fully_qualified_role_assignment_id2,
            'scope': scope,
            'principal_id': principal_id
        })

        self.cmd('az cosmosdb create -n {acc} -g {rg} --locations regionName=eastus2')
        self.cmd('az cosmosdb sql database create -g {rg} -a {acc} -n {db_name}')
        self.cmd('az cosmosdb sql role definition create -g {rg} -a {acc} -b "{create_body}"', checks=[
            self.check('id', fully_qualified_role_def_id),
            self.check('roleName', 'roleName'),
            self.check('sqlRoleDefinitionGetResultsType', 'CustomRole'),
            self.check('assignableScopes[0]', assignable_scope),
            self.check('length(permissions)', 1)
        ])

        assert self.cmd('az cosmosdb sql role definition exists -g {rg} -a {acc} -i {role_def_id}').get_output_in_json()

        self.cmd('az cosmosdb sql role definition show -g {rg} -a {acc} -i {role_def_id}', checks=[
            self.check('roleName', 'roleName')
        ])

        self.cmd('az cosmosdb sql role definition update -g {rg} -a {acc} -b "{update_body}"', checks=[
            self.check('id', fully_qualified_role_def_id),
            self.check('roleName', 'roleName2'),
            self.check('sqlRoleDefinitionGetResultsType', 'CustomRole'),
            self.check('assignableScopes[0]', assignable_scope),
            self.check('length(permissions)', 2)
        ])

        self.cmd('az cosmosdb sql role definition create -g {rg} -a {acc} -b "{create_body2}"', checks=[
            self.check('id', fully_qualified_role_def_id2),
            self.check('roleName', 'roleName3'),
            self.check('sqlRoleDefinitionGetResultsType', 'CustomRole'),
            self.check('assignableScopes[0]', assignable_scope),
            self.check('length(permissions)', 3)
        ])

        role_definition_list = self.cmd('az cosmosdb sql role definition list -g {rg} -a {acc}').get_output_in_json()
        assert len(role_definition_list) == 2

        self.cmd('az cosmosdb sql role assignment create -g {rg} -a {acc} -s {scope} -p {principal_id} -d {fully_qualified_role_def_id} -i {role_assignment_id}', checks=[
            self.check('id', fully_qualified_role_assignment_id),
            self.check('roleDefinitionId', fully_qualified_role_def_id),
            self.check('scope', scope),
            self.check('principalId', principal_id)
        ])

        assert self.cmd('az cosmosdb sql role assignment exists -g {rg} -a {acc} -i {role_assignment_id}').get_output_in_json()

        self.cmd('az cosmosdb sql role assignment show -g {rg} -a {acc} -i {role_assignment_id}', checks=[
            self.check('id', fully_qualified_role_assignment_id)
        ])

        self.cmd('az cosmosdb sql role assignment update -g {rg} -a {acc} -d {role_def_id2} -i {fully_qualified_role_assignment_id}', checks=[
            self.check('id', fully_qualified_role_assignment_id),
            self.check('roleDefinitionId', fully_qualified_role_def_id2),
            self.check('scope', scope),
            self.check('principalId', principal_id)
        ])

        self.cmd('az cosmosdb sql role assignment create -g {rg} -a {acc} -s {scope} -p {principal_id} -n roleName2 -i {role_assignment_id2}', checks=[
            self.check('id', fully_qualified_role_assignment_id2),
            self.check('roleDefinitionId', fully_qualified_role_def_id),
            self.check('scope', scope),
            self.check('principalId', principal_id)
        ])

        role_assignment_list = self.cmd('az cosmosdb sql role assignment list -g {rg} -a {acc}').get_output_in_json()
        assert len(role_assignment_list) == 2

        self.cmd('az cosmosdb sql role assignment delete -g {rg} -a {acc} -i {role_assignment_id} --yes')
        self.cmd('az cosmosdb sql role assignment delete -g {rg} -a {acc} -i {role_assignment_id2} --yes')
        role_assignment_list = self.cmd('az cosmosdb sql role assignment list -g {rg} -a {acc}').get_output_in_json()
        assert len(role_assignment_list) == 0

        self.cmd('az cosmosdb sql role definition delete -g {rg} -a {acc} -i {role_def_id} --yes')
        self.cmd('az cosmosdb sql role definition delete -g {rg} -a {acc} -i {fully_qualified_role_def_id2} --yes')
        role_definition_list = self.cmd('az cosmosdb sql role definition list -g {rg} -a {acc}').get_output_in_json()
        assert len(role_definition_list) == 0
