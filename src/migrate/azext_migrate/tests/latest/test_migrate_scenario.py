# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class AzureMigrateScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_migrate')
    def test_migrate(self, resource_group):

        self.cmd('az migrate projects create '
                 '--resource-group "myResourceGroup" '
                 '--project-name "project01" '
                 '--project "test"'
                 '--e-tag "\"b701c73a-0000-0000-0000-59c12ff00000\"" '
                 '--location "West Us" '
                 '--customer-workspace-id "url-to-customers-service-map" '
                 '--customer-workspace-location "West Us"',
                 checks=[])

        self.cmd('az migrate group create '
                 '--resource-group-name "myResourceGroup" '
                 '--project-name "project01" '
                 '--group-name "group01" '
                 '--e-tag "\"1100637e-0000-0000-0000-59f6ed1f0000\"" '
                 '--machines "/subscriptions/75dd7e42-4fd1-4512-af04-83ad9864335b/resourceGroups/myResourceGroup/providers/Microsoft.Migrate/projects/project01/machines/amansing_vm1,/subscriptions/75dd7e42-4fd1-4512-af04-83ad9864335b/resourceGroups/myResourceGroup/providers/Microsoft.Migrate/projects/project01/machines/amansing_vm2,/subscriptions/75dd7e42-4fd1-4512-af04-83ad9864335b/resourceGroups/myResourceGroup/providers/Microsoft.Migrate/projects/project01/machines/amansing_vm3"',
                 checks=[])

        self.cmd('az migrate assessment create '
                 '--resource-group-name "myResourceGroup" '
                 '--project-name "project01" '
                 '--group-name "group01" '
                 '--assessment-name "assessment01" '
                 '--e-tag "\"1100637e-0000-0000-0000-59f6ed1f0000\"" '
                 '--azure-location "WestUs" '
                 '--azure-offer-code "MSAZR0003P" '
                 '--azure-pricing-tier "Standard" '
                 '--azure-storage-redundancy "LocallyRedundant" '
                 '--scaling-factor "1.2" '
                 '--percentile "Percentile50" '
                 '--time-range "Day" '
                 '--stage "InProgress" '
                 '--currency "USD" '
                 '--azure-hybrid-use-benefit "Yes" '
                 '--discount-percentage "100" '
                 '--sizing-criterion "PerformanceBased"',
                 checks=[])

        self.cmd('az migrate assessed-machine get '
                 '--resource-group-name "myResourceGroup" '
                 '--project-name "project01" '
                 '--group-name "group01" '
                 '--assessment-name "assessment01"',
                 checks=[])

        self.cmd('az migrate assessed-machine list-by-assessment '
                 '--resource-group-name "myResourceGroup" '
                 '--project-name "project01" '
                 '--group-name "group01" '
                 '--assessment-name "assessment01"',
                 checks=[])

        self.cmd('az migrate assessment show '
                 '--resource-group-name "myResourceGroup" '
                 '--project-name "project01" '
                 '--group-name "group01" '
                 '--assessment-name "assessment01"',
                 checks=[])

        self.cmd('az migrate assessment list '
                 '--resource-group-name "myResourceGroup" '
                 '--project-name "project01" '
                 '--group-name "group01"',
                 checks=[])

        self.cmd('az migrate machine get '
                 '--resource-group-name "myResourceGroup" '
                 '--project-name "project01"',
                 checks=[])

        self.cmd('az migrate group show '
                 '--resource-group-name "myResourceGroup" '
                 '--project-name "project01" '
                 '--group-name "group01"',
                 checks=[])

        self.cmd('az migrate assessment list-by-project '
                 '--resource-group-name "myResourceGroup" '
                 '--project-name "project01"',
                 checks=[])

        self.cmd('az migrate machine list-by-project '
                 '--resource-group-name "myResourceGroup" '
                 '--project-name "project01"',
                 checks=[])

        self.cmd('az migrate group list '
                 '--resource-group-name "myResourceGroup" '
                 '--project-name "project01"',
                 checks=[])

        self.cmd('az migrate project show '
                 '--resource-group-name "myResourceGroup" '
                 '--project-name "project01"',
                 checks=[])

        self.cmd('az migrate assessment-option get '
                 '--location-name "SoutheastAsia"',
                 checks=[])

        self.cmd('az migrate project list '
                 '--resource-group-name "myResourceGroup"',
                 checks=[])

        self.cmd('az migrate project list '
                 '--resource-group-name "myResourceGroup"',
                 checks=[])

        self.cmd('az migrate operation list',
                 checks=[])

        self.cmd('az migrate assessment get-report-download-url '
                 '--resource-group-name "myResourceGroup" '
                 '--project-name "project01" '
                 '--group-name "group01" '
                 '--assessment-name "assessment01"',
                 checks=[])

        self.cmd('az migrate project get-keys '
                 '--resource-group-name "myResourceGroup" '
                 '--project-name "project01"',
                 checks=[])

        self.cmd('az migrate project update '
                 '--resource-group-name "myResourceGroup" '
                 '--project-name "project01" '
                 '--e-tag "" '
                 '--location "West Us" '
                 '--customer-workspace-id "url-to-customers-service-map" '
                 '--customer-workspace-location "West Us"',
                 checks=[])

        self.cmd('az migrate location check-name-availability '
                 '--location-name "eastus" '
                 '--name "newprojectname" '
                 '--type "Microsoft.Migrate/projects"',
                 checks=[])

        self.cmd('az migrate location check-name-availability '
                 '--location-name "eastus" '
                 '--name "existingprojectname" '
                 '--type "Microsoft.Migrate/projects"',
                 checks=[])

        self.cmd('az migrate assessment delete '
                 '--resource-group-name "myResourceGroup" '
                 '--project-name "project01" '
                 '--group-name "group01" '
                 '--assessment-name "assessment01"',
                 checks=[])

        self.cmd('az migrate group delete '
                 '--resource-group-name "myResourceGroup" '
                 '--project-name "project01" '
                 '--group-name "group01"',
                 checks=[])

        self.cmd('az migrate project delete '
                 '--resource-group-name "myResourceGroup" '
                 '--project-name "project01"',
                 checks=[])
