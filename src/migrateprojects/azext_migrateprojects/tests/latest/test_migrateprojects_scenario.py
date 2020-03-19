# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk import ResourceGroupPreparer


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class AzureMigrateHubScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_migrateprojects_myResourceGroup'[:9], key='rg')
    def test_migrateprojects(self, resource_group):

        self.cmd('az migrateprojects database-instance show '
                 '--database-instance-name "{myinstance}" '
                 '--migrate-project-name "{project01}" '
                 '--resource-group "{rg}"',
                 checks=[])

        self.cmd('az migrateprojects event show '
                 '--event-name "{MigrateEvent01}" '
                 '--migrate-project-name "{project01}" '
                 '--resource-group "{rg}"',
                 checks=[])

        self.cmd('az migrateprojects database show '
                 '--database-name "mydb" '
                 '--migrate-project-name "{project01}" '
                 '--resource-group "{rg}"',
                 checks=[])

        self.cmd('az migrateprojects solution show '
                 '--migrate-project-name "{project01}" '
                 '--resource-group "{rg}" '
                 '--solution-name "{dbsolution}"',
                 checks=[])

        self.cmd('az migrateprojects machine show '
                 '--machine-name "{vm1}" '
                 '--migrate-project-name "{project01}" '
                 '--resource-group "{rg}"',
                 checks=[])

        self.cmd('az migrateprojects migrate-project show '
                 '--migrate-project-name "{project01}" '
                 '--resource-group "{rg}"',
                 checks=[])

        self.cmd('az migrateprojects solution cleanup-solution-data '
                 '--migrate-project-name "{project01}" '
                 '--resource-group "{rg}" '
                 '--solution-name "{Solutions_2}"',
                 checks=[])

        self.cmd('az migrateprojects solution get-config '
                 '--migrate-project-name "{project01}" '
                 '--resource-group "{rg}" '
                 '--solution-name "{Solutions_2}"',
                 checks=[])

        self.cmd('az migrateprojects solution patch-solution '
                 '--migrate-project-name "{project01}" '
                 '--resource-group "{rg}" '
                 '--properties "{{\\"status\\":\\"Active\\"}}" '
                 '--solution-name "{dbsolution}"',
                 checks=[])

        self.cmd('az migrateprojects solution put-solution '
                 '--migrate-project-name "{project01}" '
                 '--resource-group "{rg}" '
                 '--properties "{{\\"goal\\":\\"Databases\\",\\"purpose\\":\\"Assessment\\",\\"tool\\":\\"DataMigrationAssistant\\"}}" '
                 '--solution-name "{dbsolution}"',
                 checks=[])

        self.cmd('az migrateprojects database-instance enumerate-database-instance '
                 '--migrate-project-name "{project01}" '
                 '--resource-group "{rg}"',
                 checks=[])

        self.cmd('az migrateprojects migrate-project refresh-migrate-project-summary '
                 '--goal "Servers" '
                 '--migrate-project-name "{project01}" '
                 '--resource-group "{rg}"',
                 checks=[])

        self.cmd('az migrateprojects event enumerate-event '
                 '--migrate-project-name "{project01}" '
                 '--resource-group "{rg}"',
                 checks=[])

        self.cmd('az migrateprojects migrate-project register-tool '
                 '--tool "ServerMigration" '
                 '--migrate-project-name "{project01}" '
                 '--resource-group "{rg}"',
                 checks=[])

        self.cmd('az migrateprojects solution enumerate-solution '
                 '--migrate-project-name "{project01}" '
                 '--resource-group "{rg}"',
                 checks=[])

        self.cmd('az migrateprojects database enumerate-database '
                 '--migrate-project-name "{project01}" '
                 '--resource-group "{rg}"',
                 checks=[])

        self.cmd('az migrateprojects machine enumerate-machine '
                 '--migrate-project-name "{project01}" '
                 '--resource-group "{rg}"',
                 checks=[])

        self.cmd('az migrateprojects migrate-project put-migrate-project '
                 '--e-tag "\\"b701c73a-0000-0000-0000-59c12ff00000\\"" '
                 '--location "Southeast Asia" '
                 '--properties "{{}}" '
                 '--migrate-project-name "{project01}" '
                 '--resource-group "{rg}"',
                 checks=[])

        self.cmd('az migrateprojects migrate-project patch-migrate-project '
                 '--e-tag "\\"b701c73a-0000-0000-0000-59c12ff00000\\"" '
                 '--location "Southeast Asia" '
                 '--properties "{{\\"registeredTools\\":[\\"ServerMigration\\"]}}" '
                 '--migrate-project-name "{project01}" '
                 '--resource-group "{rg}"',
                 checks=[])

        self.cmd('az migrateprojects event delete '
                 '--event-name "{MigrateEvent01}" '
                 '--migrate-project-name "{project01}" '
                 '--resource-group "{rg}"',
                 checks=[])

        self.cmd('az migrateprojects solution delete '
                 '--migrate-project-name "{project01}" '
                 '--resource-group "{rg}" '
                 '--solution-name "{Solutions_2}"',
                 checks=[])

        self.cmd('az migrateprojects migrate-project delete '
                 '--migrate-project-name "{project01}" '
                 '--resource-group "{rg}"',
                 checks=[])
