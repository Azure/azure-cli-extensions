# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.testsdk import (ScenarioTest, JMESPathCheck, ResourceGroupPreparer,
                               api_version_constraint)


class DbUpTests(ScenarioTest):
    def test_mysql_flow(self):
        output = self.cmd('mysql up').get_output_in_json()
        print(output)
        output = self.cmd('mysql up').get_output_in_json()
        
        raise Exception
    
    def test_postgres_flow(self):
        output = self.cmd('postgres up').get_output_in_json()
        print(output)
        user, server = output.username.split('@')
        password, database = output['password'], 'sampledb'
        output2 = self.cmd('postgres up').get_output_in_json()
        print(output2)
        self.cmd('postgres down --no-wait -y --delete-group')
        output3 = self.cmd('postgres show-connection-string').get_output_in_json()
        print(output3)
        raise Exception
