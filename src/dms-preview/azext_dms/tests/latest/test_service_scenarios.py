# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from azure.cli.testsdk import (ScenarioTest,
                               ResourceGroupPreparer,
                               VirtualNetworkPreparer,
                               JMESPathCheck)


class DmsServiceTests(ScenarioTest):
    service_random_name_prefix = 'dmsextclitest'
    location_name = 'centralus'
    sku_name = 'Premium_4vCores'
    vsubnet_rg = 'ERNetwork'
    vsubnet_vn = 'AzureDMS-CORP-USC-VNET-5044'
    vsubnet_sn = 'Subnet-1'
    name_exists_checks = [JMESPathCheck('nameAvailable', False),
                          JMESPathCheck('reason', 'AlreadyExists')]
    name_available_checks = [JMESPathCheck('nameAvailable', True)]

    @ResourceGroupPreparer(name_prefix='dmsext_cli_test_', location=location_name)
    @VirtualNetworkPreparer(name_prefix='dmsext.clitest.vn')
    def test_project_commands(self, resource_group):
        service_name = self.create_random_name(self.service_random_name_prefix, 20)
        project_name1 = self.create_random_name('project1', 15)
        project_name2 = self.create_random_name('project2', 15)
        project_name_pg = self.create_random_name('projectpg', 20)
        project_name_mg = self.create_random_name('projectmg', 20)

        self.kwargs.update({
            'vsubnet_rg': self.vsubnet_rg,
            'vsubnet_vn': self.vsubnet_vn,
            'vsubnet_sn': self.vsubnet_sn
        })
        subnet = self.cmd(("az network vnet subnet show "
                           "-g {vsubnet_rg} "
                           "-n {vsubnet_sn} "
                           "--vnet-name {vsubnet_vn}")).get_output_in_json()

        self.kwargs.update({
            'lname': self.location_name,
            'skuname': self.sku_name,
            'vnetid': subnet['id'],
            'sname': service_name,
            'pname1': project_name1,
            'pname2': project_name2,
            'pnamepg': project_name_pg,
            'pnamemg': project_name_mg
        })

        # Set up container service
        self.cmd(("az dms create "
                  "-l {lname} "
                  "-n {sname} "
                  "-g {rg} "
                  "--sku-name {skuname} "
                  "--subnet {vnetid} "
                  "--tags area=cli env=test"))

        self.cmd(("az dms project show "
                  "-g {rg} "
                  "--service-name {sname} "
                  "-n {pname1}"),
                 expect_failure=True)

        create_checks = [JMESPathCheck('location', self.location_name),
                         JMESPathCheck('resourceGroup', resource_group),
                         JMESPathCheck('name', project_name1),
                         JMESPathCheck('sourcePlatform', 'SQL'),
                         JMESPathCheck('targetPlatform', 'SQLDB'),
                         JMESPathCheck('provisioningState', 'Succeeded'),
                         JMESPathCheck('tags.Cli', ''),
                         JMESPathCheck('tags.Type', 'test'),
                         JMESPathCheck('type', 'Microsoft.DataMigration/services/projects')]
        self.cmd(("az dms project create "
                  "-g {rg} "
                  "--service-name {sname} "
                  "-l {lname} "
                  "-n {pname1} "
                  "--source-platform SQL "
                  "--target-platform SQLDB "
                  "--tags Type=test Cli"),
                 checks=create_checks)

        self.cmd(("az dms project show "
                  "-g {rg} "
                  "--service-name {sname} "
                  "-n {pname1}"),
                 create_checks)

        # Test PostgreSQL project creation and deletion
        create_checks_pg = [JMESPathCheck('location', self.location_name),
                            JMESPathCheck('resourceGroup', resource_group),
                            JMESPathCheck('name', project_name_pg),
                            JMESPathCheck('sourcePlatform', 'PostgreSQL'),
                            JMESPathCheck('targetPlatform', 'AzureDbForPostgreSQL'),
                            JMESPathCheck('provisioningState', 'Succeeded'),
                            JMESPathCheck('tags.Cli', ''),
                            JMESPathCheck('tags.Type', 'test'),
                            JMESPathCheck('type', 'Microsoft.DataMigration/services/projects')]
        self.cmd(("az dms project create "
                  "-g {rg} "
                  "--service-name {sname} "
                  "-l {lname} "
                  "-n {pnamepg} "
                  "--source-platform PostgreSQL "
                  "--target-platform AzureDbForPostgreSQL "
                  "--tags Type=test Cli"),
                 checks=create_checks_pg)
        self.cmd(("az dms project show "
                  "-g {rg} "
                  "--service-name {sname} "
                  "-n {pnamepg}"),
                 create_checks_pg)

        # Test MongoDb project creation and deletion
        create_checks_mg = [JMESPathCheck('location', self.location_name),
                            JMESPathCheck('resourceGroup', resource_group),
                            JMESPathCheck('name', project_name_mg),
                            JMESPathCheck('sourcePlatform', 'MongoDb'),
                            JMESPathCheck('targetPlatform', 'MongoDb'),
                            JMESPathCheck('provisioningState', 'Succeeded'),
                            JMESPathCheck('tags.Cli', ''),
                            JMESPathCheck('tags.Type', 'test'),
                            JMESPathCheck('type', 'Microsoft.DataMigration/services/projects')]
        self.cmd(("az dms project create "
                  "-g {rg} "
                  "--service-name {sname} "
                  "-l {lname} "
                  "-n {pnamemg} "
                  "--source-platform MongoDb "
                  "--target-platform MongoDb "
                  "--tags Type=test Cli"),
                 checks=create_checks_mg)
        self.cmd(("az dms project show "
                  "-g {rg} "
                  "--service-name {sname} "
                  "-n {pnamemg}"),
                 create_checks_mg)

        create_checks_notags = [JMESPathCheck('tags', None)]
        self.cmd(("az dms project create "
                  "-g {rg} "
                  "--service-name {sname} "
                  "-l {lname} "
                  "-n {pname2} "
                  "--source-platform SQL "
                  "--target-platform SQLDB"),
                 checks=create_checks_notags)

        list_checks = [JMESPathCheck('length(@)', 4),
                       JMESPathCheck("length([?name == '{}'])".format(project_name1), 1)]
        self.cmd(("az dms project list "
                  "-g {rg} "
                  "--service-name {sname}"),
                 list_checks)

        self.cmd(("az dms project check-name "
                  "-g {rg} "
                  "--service-name {sname} "
                  "-n {pname2}"),
                 checks=self.name_exists_checks)

        self.cmd(("az dms project delete "
                  "-g {rg} "
                  "--service-name {sname} "
                  "-n {pname2} -y"))

        self.cmd(("az dms project check-name "
                  "-g {rg} "
                  "--service-name {sname} "
                  "-n {pname2}"),
                 checks=self.name_available_checks)

        # Clean up service for live runs
        self.cmd(("az dms delete "
                  "-g {rg} "
                  "-n {sname} "
                  "--delete-running-tasks true -y"))

    @ResourceGroupPreparer(name_prefix='dms_cli_test_', location=location_name)
    @VirtualNetworkPreparer(name_prefix='dms.clitest.vn')
    def test_task_commands(self, resource_group):
        from azure.cli.testsdk.checkers import JMESPathPatternCheck

        local_vars = {
            "service_name": self.create_random_name(self.service_random_name_prefix, 20),
            "project_name": self.create_random_name('project', 15),
            "task_name1": self.create_random_name('task1', 15),
            "task_name2": self.create_random_name('task2', 15),
            "database_options1": ("[ { 'name': 'SourceDatabase1', 'target_database_name': 'TargetDatabase1', "
                                  "'make_source_db_read_only': False, 'table_map': { 'dbo.TestTableSource1': "
                                  "'dbo.TestTableTarget1', 'dbo.TestTableSource2': 'dbo.TestTableTarget2' } } ]"),
            "database_options2": ("[ { 'name': 'SourceDatabase2', 'target_database_name': 'TargetDatabase2', "
                                  "'make_source_db_read_only': False, 'table_map': { 'dbo.TestTableSource1': "
                                  "'dbo.TestTableTarget1', 'dbo.TestTableSource2': 'dbo.TestTableTarget2' } } ]"),
            "source_connection_info": ("{ 'userName': 'testuser', 'password': 'testpassword', 'dataSource': "
                                       "'notarealsourceserver', 'authentication': 'SqlAuthentication', "
                                       "'encryptConnection': True, 'trustServerCertificate': True }"),
            "target_connection_info": ("{ 'userName': 'testuser', 'password': 'testpassword', 'dataSource': "
                                       "'notarealtargetserver', 'authentication': 'SqlAuthentication', "
                                       "'encryptConnection': True, 'trustServerCertificate': True }"),
            "project_name_pg": self.create_random_name('projectpg', 20),
            "task_name_pg": self.create_random_name('taskpg', 20),
            "source_connection_info_pg": ("{ 'userName': 'testuser', 'password': 'testpassword', 'serverName': "
                                          "'notarealsourceserver', 'databaseName': 'notarealdatabasename', "
                                          "'encryptConnection': False, 'trustServerCertificate': True }"),
            "target_connection_info_pg": ("{ 'userName': 'testuser', 'password': 'testpassword', 'serverName': "
                                          "'notarealtargetserver', 'databaseName': 'notarealdatabasename'}"),
            "database_options_pg": ("[ { 'name': 'SourceDatabase1', 'target_database_name': 'TargetDatabase1', "
                                    "'selectedTables': [ 'public.TestTableSource1', 'public.TestTableSource2'] } ]"),
            "project_name_mg": self.create_random_name('projectmg', 20),
            "task_name_mgv": self.create_random_name('taskmgv', 20),
            "source_connection_info_mg": ("{ 'userName': 'mongoadmin', "
                                          "'password': 'password', "
                                          "'connectionString': 'mongodb://127.0.0.1:27017'}"),
            "target_connection_info_mg": ("{ 'userName': 'mongoadmin', "
                                          "'password': 'password', "
                                          "'connectionString': 'mongodb://127.0.0.1:27017'}"),
            "database_options_mg": ("{ \"boostRUs\": 0, \"replication\": \"OneTime\", "
                                    "\"throttling\": { \"minFreeCpu\": 25, \"minFreeMemoryMb\": 1024, "
                                    "\"maxParallelism\": 2 }, \"databases\": {\"db1\": {\"targetRUs\": 0, "
                                    "\"collections\": { \"cdb11\": {\"canDelete\": true, \"shardKey\": null, "
                                    "\"targetRUs\": null }, \"cdb12\": {\"canDelete\": true, \"shardKey\": null, "
                                    "\"targetRUs\": null }}},\"db2\": {\"targetRUs\": 0, \"collections\": { "
                                    "\"cdb21\": {\"canDelete\": true, \"shardKey\": null, \"targetRUs\": null }, "
                                    "\"cdb22\": {\"canDelete\": true, \"shardKey\": null, \"targetRUs\": null }}}}}")
        }

        self.kwargs.update({
            'vsubnet_rg': self.vsubnet_rg,
            'vsubnet_vn': self.vsubnet_vn,
            'vsubnet_sn': self.vsubnet_sn
        })
        subnet = self.cmd(("az network vnet subnet show "
                           "-g {vsubnet_rg} "
                           "-n {vsubnet_sn} "
                           "--vnet-name {vsubnet_vn}")).get_output_in_json()



        self.kwargs.update({
            'lname': self.location_name,
            'skuname': self.sku_name,
            'vnetid': subnet['id'],
            'sname': local_vars["service_name"],
            'pname': local_vars["project_name"],
            'pnamepg': local_vars["project_name_pg"],
            'pnamemg': local_vars["project_name_mg"],
            'tname1': local_vars["task_name1"],
            'tname2': local_vars["task_name2"],
            'tnamepg': local_vars["task_name_pg"],
            'tnamemgv': local_vars["task_name_mgv"],
            'dboptions1': local_vars["database_options1"],
            'dboptions2': local_vars["database_options2"],
            'dboptionspg': local_vars["database_options_pg"],
            'dboptionsmg': local_vars["database_options_mg"],
            'sconn': local_vars["source_connection_info"],
            'sconnpg': local_vars["source_connection_info_pg"],
            'sconnmg': local_vars["source_connection_info_mg"],
            'tconn': local_vars["target_connection_info"],
            'tconnpg': local_vars["target_connection_info_pg"],
            'tconnmg': local_vars["target_connection_info_mg"]
        })

        # Set up container service and project
        self.cmd(("az dms create "
                  "-l {lname} "
                  "-n {sname} "
                  "-g {rg} "
                  "--sku-name {skuname} "
                  "--subnet {vnetid} "
                  "--tags area=cli env=test"))
        self.cmd(("az dms project create "
                  "-g {rg} "
                  "--service-name {sname} "
                  "-l {lname} "
                  "-n {pname} "
                  "--source-platform SQL "
                  "--target-platform SQLDB"))
        self.cmd(("az dms project create "
                  "-g {rg} "
                  "--service-name {sname} "
                  "-l {lname} "
                  "-n {pnamepg} "
                  "--source-platform PostgreSQL "
                  "--target-platform AzureDbForPostgreSQL"))
        self.cmd(("az dms project create "
                  "-g {rg} "
                  "--service-name {sname} "
                  "-l {lname} "
                  "-n {pnamemg} "
                  "--source-platform MongoDb "
                  "--target-platform MongoDb "))

        self.cmd(("az dms project task show "
                  "-g {rg} "
                  "--service-name {sname} "
                  "--project-name {pname} "
                  "-n {tname1}"),
                 expect_failure=True)
        self.cmd(("az dms project task show "
                  "-g {rg} "
                  "--service-name {sname} "
                  "--project-name {pnamepg} "
                  "-n {tnamepg}"),
                 expect_failure=True)
        self.cmd(("az dms project task show "
                  "-g {rg} "
                  "--service-name {sname} "
                  "--project-name {pnamemg} "
                  "-n {tnamemgv}"),
                 expect_failure=True)

        create_checks = [JMESPathCheck('name', local_vars["task_name1"]),
                         JMESPathCheck('resourceGroup', resource_group),
                         JMESPathCheck('type', 'Microsoft.DataMigration/services/projects/tasks'),
                         JMESPathCheck('length(properties.input.selectedDatabases[0].tableMap)', 2),
                         JMESPathCheck('properties.input.sourceConnectionInfo.dataSource', 'notarealsourceserver'),
                         JMESPathCheck('properties.input.targetConnectionInfo.dataSource', 'notarealtargetserver'),
                         JMESPathCheck('properties.taskType', 'Migrate.SqlServer.SqlDb'),
                         JMESPathCheck('properties.input.validationOptions.enableDataIntegrityValidation', False),
                         JMESPathCheck('properties.input.validationOptions.enableQueryAnalysisValidation', False),
                         JMESPathCheck('properties.input.validationOptions.enableSchemaValidation', False)]
        cancel_checks = [JMESPathCheck('name', local_vars["task_name1"]),
                         JMESPathPatternCheck('properties.state', 'Cancel(?:ed|ing)')]
        create_checks_pg = [JMESPathCheck('name', local_vars["task_name_pg"]),
                            JMESPathCheck('resourceGroup', resource_group),
                            JMESPathCheck('type', 'Microsoft.DataMigration/services/projects/tasks'),
                            JMESPathCheck('length(properties.input.selectedDatabases[0].selectedTables)', 2),
                            JMESPathCheck('properties.input.sourceConnectionInfo.serverName', 'notarealsourceserver'),
                            JMESPathCheck('properties.input.sourceConnectionInfo.encryptConnection', False),
                            JMESPathCheck('properties.input.sourceConnectionInfo.trustServerCertificate', True),
                            JMESPathCheck('properties.input.targetConnectionInfo.serverName', 'notarealtargetserver'),
                            JMESPathCheck('properties.input.targetConnectionInfo.encryptConnection', True),
                            JMESPathCheck('properties.input.targetConnectionInfo.trustServerCertificate', False),
                            JMESPathCheck('properties.taskType', 'Migrate.PostgreSql.AzureDbForPostgreSql.SyncV2')]
        cancel_checks_pg = [JMESPathCheck('name', local_vars["task_name_pg"]),
                            JMESPathPatternCheck('properties.state', 'Cancel(?:ed|ing)')]
        create_checks_mgv = [JMESPathCheck('name', local_vars["task_name_mgv"]),
                             JMESPathCheck('resourceGroup', resource_group),
                             JMESPathCheck('type', 'Microsoft.DataMigration/services/projects/tasks'),
                             JMESPathCheck('properties.input.throttling.maxParallelism', 2),
                             JMESPathCheck('properties.input.throttling.minFreeCpu', 25),
                             JMESPathCheck('properties.input.throttling.minFreeMemoryMb', 1024),
                             JMESPathCheck('properties.input.replication', 'OneTime'),
                             JMESPathCheck('length(properties.input.databases)', 2),
                             JMESPathCheck('properties.input.databases.db1.targetRUs', 0),
                             JMESPathCheck('length(properties.input.databases.db1.collections)', 2),
                             JMESPathCheck('properties.input.databases.db1.collections.cdb11.canDelete', True),
                             JMESPathCheck('properties.input.databases.db1.collections.cdb11.shardKey', 'None'),
                             JMESPathCheck('properties.input.databases.db1.collections.cdb11.targetRUs', 'None'),
                             JMESPathCheck('properties.input.databases.db1.collections.cdb12.canDelete', True),
                             JMESPathCheck('properties.input.databases.db1.collections.cdb12.shardKey', 'None'),
                             JMESPathCheck('properties.input.databases.db1.collections.cdb12.targetRUs', 'None'),
                             JMESPathCheck('properties.input.databases.db2.targetRUs', 0),
                             JMESPathCheck('length(properties.input.databases.db2.collections)', 2),
                             JMESPathCheck('properties.input.databases.db2.collections.cdb21.canDelete', True),
                             JMESPathCheck('properties.input.databases.db2.collections.cdb21.shardKey', 'None'),
                             JMESPathCheck('properties.input.databases.db2.collections.cdb21.targetRUs', 'None'),
                             JMESPathCheck('properties.input.databases.db2.collections.cdb22.canDelete', True),
                             JMESPathCheck('properties.input.databases.db2.collections.cdb22.shardKey', 'None'),
                             JMESPathCheck('properties.input.databases.db2.collections.cdb22.targetRUs', 'None'),
                             JMESPathCheck('properties.input.source.type', 'MongoDbConnectionInfo'),
                             JMESPathCheck('properties.input.source.userName', 'mongoadmin'),
                             JMESPathCheck('properties.input.target.type', 'MongoDbConnectionInfo'),
                             JMESPathCheck('properties.input.target.userName', 'mongoadmin'),
                             JMESPathCheck('properties.taskType', 'Validate.MongoDb')]

        # SQL Tests
        self.cmd(("az dms project task create "
                  "--task-type OfflineMigration "
                  "--database-options-json \"{dboptions1}\" "
                  "-n {tname1} "
                  "--project-name {pname} "
                  "-g {rg} "
                  "--service-name {sname} "
                  "--source-connection-json \"{sconn}\" "
                  "--target-connection-json \"{tconn}\""),
                 checks=create_checks)
        self.cmd(("az dms project task show "
                  "-g {rg} "
                  "--service-name {sname} "
                  "--project-name {pname} "
                  "-n {tname1}"),
                 checks=create_checks)
        self.cmd(("az dms project task cancel "
                  "-g {rg} "
                  "--service-name {sname} "
                  "--project-name {pname} "
                  "-n {tname1}"),
                 checks=cancel_checks)

        # PG Tests
        self.cmd(("az dms project task create "
                  "--task-type OnlineMigration "
                  "--database-options-json \"{dboptionspg}\" "
                  "-n {tnamepg} "
                  "--project-name {pnamepg} "
                  "-g {rg} "
                  "--service-name {sname} "
                  "--source-connection-json \"{sconnpg}\" "
                  "--target-connection-json \"{tconnpg}\""),
                 checks=create_checks_pg)
        self.cmd(("az dms project task show "
                  "-g {rg} "
                  "--service-name {sname} "
                  "--project-name {pnamepg} "
                  "-n {tnamepg}"),
                 checks=create_checks_pg)
        self.cmd(("az dms project task cancel "
                  "-g {rg} "
                  "--service-name {sname} "
                  "--project-name {pnamepg} "
                  "-n {tnamepg}"),
                 checks=cancel_checks_pg)

        self.cmd(("az dms project task create "
                  "--task-type OfflineMigration "
                  "--database-options-json \"{dboptions2}\" "
                  "-n {tname2} "
                  "--project-name {pname} "
                  "-g {rg} "
                  "--service-name {sname} "
                  "--source-connection-json \"{sconn}\" "
                  "--target-connection-json \"{tconn}\""))

        # Mongo Tests
        self.cmd(("az dms project task create "
                  "--task-type OfflineMigration "
                  "--database-options-json '{dboptionsmg}' "
                  "-n {tnamemgv} "
                  "--project-name {pnamemg} "
                  "-g {rg} "
                  "--service-name {sname} "
                  "--source-connection-json \"{sconnmg}\" "
                  "--target-connection-json \"{tconnmg}\" "
                  "--validate-only"),
                 checks=create_checks_mgv)
        self.cmd(("az dms project task show "
                  "-g {rg} "
                  "--service-name {sname} "
                  "--project-name {pnamemg} "
                  "-n {tnamemgv}"),
                 checks=create_checks_mgv)

        list_checks = [JMESPathCheck('length(@)', 2),
                       JMESPathCheck("length([?name == '{}'])".format(local_vars["task_name1"]), 1)]
        self.cmd(("az dms project task list "
                  "-g {rg} "
                  "--service-name {sname} "
                  "--project-name {pname} "
                  "--task-type \"Migrate.SqlServer.SqlDb\""),
                 checks=list_checks)

        self.cmd(("az dms project task check-name "
                  "-g {rg} "
                  "--service-name {sname} "
                  "--project-name {pname} "
                  "-n {tname1}"),
                 checks=self.name_exists_checks)

        self.cmd(("az dms project task delete "
                  "-g {rg} "
                  "--service-name {sname} "
                  "--project-name {pname} "
                  "-n {tname1} "
                  "--delete-running-tasks true -y"))

        self.cmd(("az dms project task check-name "
                  "-g {rg} "
                  "--service-name {sname} "
                  "--project-name {pname} "
                  "-n {tname1}"),
                 checks=self.name_available_checks)

        # Clean up service for live runs
        self.cmd(("az dms delete "
                  "-g {rg} "
                  "-n {sname} "
                  "--delete-running-tasks true -y"))
