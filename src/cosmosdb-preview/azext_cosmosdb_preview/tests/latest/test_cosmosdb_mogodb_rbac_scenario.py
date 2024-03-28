# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


class Cosmosdb_previewMongodbRbacScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_mongodb_role', location='westus2')
    def test_cosmosdb_mongo_role(self, resource_group):
        acc_name = self.create_random_name(prefix='cli', length=15)
        db_name = self.create_random_name(prefix='cli', length=15)

        subscription = self.get_subscription_id()
        role_def_name1 = 'my_role_def1'
        role_def_name2 = 'my_role_def2'
        role_def_id1 = db_name + '.my_role_def1'
        role_def_id2 = db_name + '.my_role_def2'
        user_definition_id = db_name + '.testUser'
        user_name = 'testUser'
        role_definition_create_body = ' {{ \\"Id\\": \\"{0}\\", \\"RoleName\\": \\"{2}\\", \\"Type\\": \\"CustomRole\\", \\"DatabaseName\\":\\"{1}\\",\\"Privileges\\":[{{\\"Resource\\":{{\\"Db\\":\\"{1}\\",\\"Collection\\":\\"test\\"}},\\"Actions\\":[\\"insert\\",\\"find\\"]}}],\\"Roles\\":[]}} '.format(
            role_def_id1, db_name, role_def_name1)
        role_definition_update_body = ' {{ \\"Id\\": \\"{0}\\", \\"RoleName\\": \\"{2}\\", \\"Type\\": \\"CustomRole\\", \\"DatabaseName\\":\\"{1}\\",\\"Privileges\\":[{{\\"Resource\\":{{\\"Db\\":\\"{1}\\",\\"Collection\\":\\"test\\"}},\\"Actions\\":[\\"find\\"]}}],\\"Roles\\":[]}} '.format(
            role_def_id1, db_name, role_def_name1)
        role_definition_create_body2 = ' {{ \\"Id\\": \\"{0}\\", \\"RoleName\\": \\"{2}\\", \\"Type\\": \\"CustomRole\\", \\"DatabaseName\\":\\"{1}\\",\\"Privileges\\":[{{\\"Resource\\":{{\\"Db\\":\\"{1}\\",\\"Collection\\":\\"test\\"}},\\"Actions\\":[\\"insert\\"]}}],\\"Roles\\":[{{\\"Role\\": \\"{3}\\",\\"Db\\": \\"{1}\\"}}]}} '.format(
            role_def_id2, db_name, role_def_name2, role_def_name1)
        user_definition_create_body = ' {{ \\"Id\\": \\"{0}\\", \\"UserName\\": \\"{2}\\", \\"Password\\": \\"MyPass\\", \\"CustomData\\": \\"MyCustomData\\", \\"DatabaseName\\":\\"{1}\\",\\"Mechanisms\\": \\"SCRAM-SHA-256\\",\\"Roles\\": [ {{\\"Role\\": \\"{3}\\",\\"Db\\": \\"{1}\\"}}]}} '.format(
            user_definition_id, db_name, user_name, role_def_name1)
        user_definition_update_body = ' {{ \\"Id\\": \\"{0}\\", \\"UserName\\": \\"{2}\\", \\"Password\\": \\"MyPass\\", \\"CustomData\\": \\"MyCustomData\\", \\"DatabaseName\\":\\"{1}\\",\\"Mechanisms\\": \\"SCRAM-SHA-256\\",\\"Roles\\": [ {{\\"Role\\": \\"{3}\\",\\"Db\\": \\"{1}\\"}}]}} '.format(
            user_definition_id, db_name, user_name, role_def_name2)
        fully_qualified_role_def_id1 = '/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.DocumentDB/databaseAccounts/{2}/mongodbRoleDefinitions/{3}'.format(
            subscription, resource_group, acc_name, role_def_id1)
        fully_qualified_role_def_id2 = '/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.DocumentDB/databaseAccounts/{2}/mongodbRoleDefinitions/{3}'.format(
            subscription, resource_group, acc_name, role_def_id2)
        fully_qualified_user_definition_id = '/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.DocumentDB/databaseAccounts/{2}/mongodbUserDefinitions/{3}'.format(
            subscription, resource_group, acc_name, user_definition_id)

        # Contract violation request body
        empty_id_role_definition_create_body = ' {{ \\"RoleName\\": \\"{1}\\", \\"Type\\": \\"CustomRole\\", \\"DatabaseName\\":\\"{0}\\",\\"Privileges\\":[{{\\"Resource\\":{{\\"Db\\":\\"{1}\\",\\"Collection\\":\\"test\\"}},\\"Actions\\":[\\"insert\\",\\"find\\"]}}],\\"Roles\\":[]}} '.format(
            db_name, role_def_name1)
        invalid_role_id_role_definition_create_body = ' {{ \\"Id\\": \\"randomid\\", \\"RoleName\\": \\"{1}\\", \\"Type\\": \\"CustomRole\\", \\"DatabaseName\\":\\"{0}\\",\\"Privileges\\":[{{\\"Resource\\":{{\\"Db\\":\\"{0}\\",\\"Collection\\":\\"test\\"}},\\"Actions\\":[\\"insert\\",\\"find\\"]}}],\\"Roles\\":[]}} '.format(
            db_name, role_def_name1)
        empty_name_role_definition_create_body = ' {{ \\"Id\\": \\"{0}\\", \\"RoleName\\": \\"\\", \\"Type\\": \\"CustomRole\\", \\"DatabaseName\\":\\"{1}\\",\\"Privileges\\":[{{\\"Resource\\":{{\\"Db\\":\\"{1}\\",\\"Collection\\":\\"test\\"}},\\"Actions\\":[\\"insert\\",\\"find\\"]}}],\\"Roles\\":[]}} '.format(
            role_def_id1, db_name)
        no_privilege_role_definition_create_body = ' {{ \\"Id\\": \\"{0}\\", \\"RoleName\\": \\"{2}\\", \\"Type\\": \\"CustomRole\\", \\"DatabaseName\\":\\"{1}\\",\\"Roles\\":[]}} '.format(
            role_def_id1, db_name, role_def_name1)
        no_resource_role_definition_create_body = ' {{ \\"Id\\": \\"{0}\\", \\"RoleName\\": \\"{2}\\", \\"Type\\": \\"CustomRole\\", \\"DatabaseName\\":\\"{1}\\",\\"Privileges\\":[{{\\"Actions\\":[\\"insert\\",\\"find\\"]}}],\\"Roles\\":[]}} '.format(
            role_def_id1, db_name, role_def_name1)
        no_actions_role_definition_create_body = ' {{ \\"Id\\": \\"{0}\\", \\"RoleName\\": \\"{2}\\", \\"Type\\": \\"CustomRole\\", \\"DatabaseName\\":\\"{1}\\",\\"Privileges\\":[{{\\"Resource\\":{{\\"Db\\":\\"{1}\\",\\"Collection\\":\\"test\\"}}}}],\\"Roles\\":[]}} '.format(
            role_def_id1, db_name, role_def_name1)
        empty_id_user_definition_create_body = ' {{ \\"Id\\": \\"\\", \\"UserName\\": \\"{1}\\", \\"Password\\": \\"MyPass\\", \\"CustomData\\": \\"MyCustomData\\", \\"DatabaseName\\":\\"{0}\\",\\"Mechanisms\\": \\"SCRAM-SHA-256\\",\\"Roles\\": [ {{\\"Role\\": \\"{2}\\",\\"Db\\": \\"{0}\\"}}]}} '.format(
            db_name, user_name, role_def_name1)
        invalid_id_user_definition_create_body = ' {{ \\"Id\\": \\"randomuserid\\", \\"UserName\\": \\"{1}\\", \\"Password\\": \\"MyPass\\", \\"CustomData\\": \\"MyCustomData\\", \\"DatabaseName\\":\\"{0}\\",\\"Mechanisms\\": \\"SCRAM-SHA-256\\",\\"Roles\\": [ {{\\"Role\\": \\"{2}\\",\\"Db\\": \\"{0}\\"}}]}} '.format(
            db_name, user_name, role_def_name1)
        empty_username_user_definition_create_body = ' {{ \\"Id\\": \\"{0}\\", \\"UserName\\": \\"\\", \\"Password\\": \\"MyPass\\", \\"CustomData\\": \\"MyCustomData\\", \\"DatabaseName\\":\\"{1}\\",\\"Mechanisms\\": \\"SCRAM-SHA-256\\",\\"Roles\\": [ {{\\"Role\\": \\"{2}\\",\\"Db\\": \\"{1}\\"}}]}} '.format(
            user_definition_id, db_name, role_def_name1)
        empty_password_user_definition_create_body = ' {{ \\"Id\\": \\"{0}\\", \\"UserName\\": \\"{2}\\", \\"Password\\": \\"\\", \\"CustomData\\": \\"MyCustomData\\", \\"DatabaseName\\":\\"{1}\\",\\"Mechanisms\\": \\"SCRAM-SHA-256\\",\\"Roles\\": [ {{\\"Role\\": \\"{3}\\",\\"Db\\": \\"{1}\\"}}]}} '.format(
            user_definition_id, db_name, user_name, role_def_name1)
        empty_db_user_definition_create_body = ' {{ \\"Id\\": \\"{0}\\", \\"UserName\\": \\"{2}\\", \\"Password\\": \\"MyPass\\", \\"CustomData\\": \\"MyCustomData\\", \\"DatabaseName\\":\\"\\",\\"Mechanisms\\": \\"SCRAM-SHA-256\\",\\"Roles\\": [ {{\\"Role\\": \\"{3}\\",\\"Db\\": \\"{1}\\"}}]}} '.format(
            user_definition_id, db_name, user_name, role_def_name1)
        no_roles_user_definition_create_body = ' {{ \\"Id\\": \\"{0}\\", \\"UserName\\": \\"{2}\\", \\"Password\\": \\"MyPass\\", \\"CustomData\\": \\"MyCustomData\\", \\"DatabaseName\\":\\"{1}\\",\\"Mechanisms\\": \\"SCRAM-SHA-256\\"}} '.format(
            user_definition_id, db_name, user_name)

        self.kwargs.update({
            'acc': acc_name,
            'db_name': db_name,
            'create_body': role_definition_create_body,
            'update_body': role_definition_update_body,
            'create_body2': role_definition_create_body2,
            'user_def_create_body': user_definition_create_body,
            'role_def_id1': role_def_id1,
            'fully_qualified_role_def_id1': fully_qualified_role_def_id1,
            'role_def_id2': role_def_id2,
            'user_name': user_name,
            'role_def_name1': role_def_name1,
            'role_def_name2': role_def_name2,
            'fully_qualified_role_def_id2': fully_qualified_role_def_id2,
            'user_definition_id': user_definition_id,
            'fully_qualified_user_definition_id': fully_qualified_user_definition_id,
            'user_definition_update_body': user_definition_update_body,
            'empty_role_def_id_body': empty_id_role_definition_create_body,
            'inalid_id_role_def_create_body': invalid_role_id_role_definition_create_body,
            'empty_role_name_create_body': empty_name_role_definition_create_body,
            'no_privilege_role_def_body': no_privilege_role_definition_create_body,
            'no_resource_role_def_body': no_resource_role_definition_create_body,
            'no_actions_role_def_body': no_actions_role_definition_create_body,
            'empty_id_user_def_create_body': empty_id_user_definition_create_body,
            'invalid_id_user_def_create_body': invalid_id_user_definition_create_body,
            'empty_username_user_def_create_body': empty_username_user_definition_create_body,
            'empty_password_user_def_create_body': empty_password_user_definition_create_body,
            'empty_db_user_def_create_body': empty_db_user_definition_create_body,
            'no_roles_user_def_create_body': no_roles_user_definition_create_body

        })

        self.cmd(
            'az cosmosdb create -n {acc} -g {rg} --kind MongoDB --capabilities EnableMongoRoleBasedAccessControl')
        self.cmd(
            'az cosmosdb mongodb database create -g {rg} -a {acc} -n {db_name}')

        # Contract Violation for Role Definition. Failure tests
        self.cmd('az cosmosdb mongodb role definition create -g {rg} -a {acc} -b "{empty_role_def_id_body}"', expect_failure=True)
        self.cmd('az cosmosdb mongodb role definition create -g {rg} -a {acc} -b "{inalid_id_role_def_create_body}"', expect_failure=True)
        self.cmd('az cosmosdb mongodb role definition create -g {rg} -a {acc} -b "{empty_role_name_create_body}"', expect_failure=True)
        self.cmd('az cosmosdb mongodb role definition create -g {rg} -a {acc} -b "{no_privilege_role_def_body}"', expect_failure=True)
        self.cmd('az cosmosdb mongodb role definition create -g {rg} -a {acc} -b "{no_resource_role_def_body}"', expect_failure=True)
        self.cmd('az cosmosdb mongodb role definition create -g {rg} -a {acc} -b "{no_actions_role_def_body}"', expect_failure=True)

        # Make sure same role def does not exist
        self.cmd(
            'az cosmosdb mongodb role definition delete -g {rg} -a {acc} -i {role_def_id1} --yes')
        role_definition_list = self.cmd(
            'az cosmosdb mongodb role definition list -g {rg} -a {acc}').get_output_in_json()
        assert len(role_definition_list) == 0

        # Success Tests
        self.cmd('az cosmosdb mongodb role definition create -g {rg} -a {acc} -b "{create_body}"', checks=[
            self.check('id', fully_qualified_role_def_id1),
            self.check('roleName', role_def_name1)
        ])

        assert self.cmd(
            'az cosmosdb mongodb role definition exists -g {rg} -a {acc} -i {role_def_id1}').get_output_in_json()

        self.cmd('az cosmosdb mongodb role definition show -g {rg} -a {acc} -i {role_def_id1}', checks=[
            self.check('roleName', role_def_name1)
        ])

        self.cmd('az cosmosdb mongodb role definition update -g {rg} -a {acc} -b "{update_body}"', checks=[
            self.check('id', fully_qualified_role_def_id1),
            self.check('length(privileges[0].actions)', 1),
            self.check('privileges[0].actions[0]', 'find')
        ])

        # Make sure same role def does not exist
        self.cmd(
            'az cosmosdb mongodb role definition delete -g {rg} -a {acc} -i {role_def_id2} --yes')
        role_definition_list = self.cmd(
            'az cosmosdb mongodb role definition list -g {rg} -a {acc}').get_output_in_json()
        assert len(role_definition_list) == 1

        self.cmd('az cosmosdb mongodb role definition create -g {rg} -a {acc} -b "{create_body2}"', checks=[
            self.check('id', fully_qualified_role_def_id2),
            self.check('roleName', role_def_name2),
        ])

        role_definition_list = self.cmd(
            'az cosmosdb mongodb role definition list -g {rg} -a {acc}').get_output_in_json()
        assert len(role_definition_list) == 2

        # User definition contract violations.
        self.cmd('az cosmosdb mongodb user definition create -g {rg} -a {acc} -b "{empty_id_user_def_create_body}"', expect_failure=True)
        self.cmd('az cosmosdb mongodb user definition create -g {rg} -a {acc} -b "{invalid_id_user_def_create_body}"', expect_failure=True)
        self.cmd('az cosmosdb mongodb user definition create -g {rg} -a {acc} -b "{empty_username_user_def_create_body}"', expect_failure=True)
        self.cmd('az cosmosdb mongodb user definition create -g {rg} -a {acc} -b "{empty_password_user_def_create_body}"', expect_failure=True)
        self.cmd('az cosmosdb mongodb user definition create -g {rg} -a {acc} -b "{empty_db_user_def_create_body}"', expect_failure=True)
        self.cmd('az cosmosdb mongodb user definition create -g {rg} -a {acc} -b "{no_roles_user_def_create_body}"', expect_failure=True)

        # Make sure same user def does not exist
        self.cmd(
            'az cosmosdb mongodb user definition delete -g {rg} -a {acc} -i {user_definition_id} --yes')
        user_def_list = self.cmd(
            'az cosmosdb mongodb user definition list -g {rg} -a {acc}').get_output_in_json()

        self.cmd('az cosmosdb mongodb user definition create -g {rg} -a {acc} -b "{user_def_create_body}"', checks=[
            self.check('id', fully_qualified_user_definition_id),
            self.check('userName', user_name),
            self.check('length(roles)', 1),
            self.check('roles[0].role', role_def_name1)
        ])

        assert self.cmd(
            'az cosmosdb mongodb user definition exists -g {rg} -a {acc} -i {user_definition_id}').get_output_in_json()

        self.cmd('az cosmosdb mongodb user definition show -g {rg} -a {acc} -i {user_definition_id}', checks=[
            self.check('id', fully_qualified_user_definition_id)
        ])

        self.cmd('az cosmosdb mongodb user definition update -g {rg} -a {acc} -b "{user_definition_update_body}"', checks=[
            self.check('id', fully_qualified_user_definition_id),
            self.check('length(roles)', 1),
            self.check('roles[0].role', 'my_role_def2')
        ])

        user_def_list = self.cmd(
            'az cosmosdb mongodb user definition list -g {rg} -a {acc}').get_output_in_json()
        assert len(user_def_list) == 1

        self.cmd(
            'az cosmosdb mongodb user definition delete -g {rg} -a {acc} -i {user_definition_id} --yes')
        user_def_list = self.cmd(
            'az cosmosdb mongodb user definition list -g {rg} -a {acc}').get_output_in_json()
        assert len(user_def_list) == 0

        self.cmd(
            'az cosmosdb mongodb role definition delete -g {rg} -a {acc} -i {role_def_id1} --yes')
        role_definition_list = self.cmd(
            'az cosmosdb mongodb role definition list -g {rg} -a {acc}').get_output_in_json()
        assert len(role_definition_list) == 1

        self.cmd(
            'az cosmosdb mongodb role definition delete -g {rg} -a {acc} -i {role_def_id2} --yes')
        role_definition_list = self.cmd(
            'az cosmosdb mongodb role definition list -g {rg} -a {acc}').get_output_in_json()
        assert len(role_definition_list) == 0
