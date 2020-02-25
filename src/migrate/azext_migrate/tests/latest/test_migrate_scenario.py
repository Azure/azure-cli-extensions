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

        self.cmd('az migrate location check-name-availability '
                 '--location-name "eastus" '
                 '--name "newprojectname"',
                 checks=[])

        self.cmd('az migrate location check-name-availability '
                 '--location-name "eastus" '
                 '--name "existingprojectname"',
                 checks=[])

        self.cmd('az migrate assessment-options show '
                 '--location-name "SoutheastAsia"',
                 checks=[])

        self.cmd('az migrate projects list '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az migrate projects list',
                 checks=[])

        self.cmd('az migrate projects show '
                 '--project-name "project01" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az migrate projects create '
                 '--e-tag "\"b701c73a-0000-0000-0000-59c12ff00000\"" '
                 '--location "West Us" '
                 '--customer-workspace-id "url-to-customers-service-map" '
                 '--customer-workspace-location "West Us" '
                 '--project-name "project01" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az migrate projects update '
                 '--e-tag "" '
                 '--location "West Us" '
                 '--customer-workspace-id "url-to-customers-service-map" '
                 '--customer-workspace-location "West Us" '
                 '--project-name "project01" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az migrate projects delete '
                 '--project-name "project01" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az migrate projects get-keys '
                 '--project-name "project01" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az migrate machines list '
                 '--project-name "project01" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az migrate machines show '
                 '--machine-name "amansing_vm1" '
                 '--project-name "project01" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az migrate groups list '
                 '--project-name "project01" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az migrate groups show '
                 '--group-name "group01" '
                 '--project-name "project01" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az migrate groups create '
                 '--e-tag "\"1100637e-0000-0000-0000-59f6ed1f0000\"" '
                 '--group-name "group01" '
                 '--project-name "project01" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az migrate groups delete '
                 '--group-name "group01" '
                 '--project-name "project01" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az migrate assessments list '
                 '--group-name "group01" '
                 '--project-name "project01" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az migrate assessments list '
                 '--project-name "project01" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az migrate assessments show '
                 '--assessment-name "assessment01" '
                 '--group-name "group01" '
                 '--project-name "project01" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az migrate assessments create '
                 '--e-tag "\"1100637e-0000-0000-0000-59f6ed1f0000\"" '
                 '--azure-hybrid-use-benefit "Yes" '
                 '--azure-location "WestUs" '
                 '--azure-offer-code "MSAZR0003P" '
                 '--azure-pricing-tier "Standard" '
                 '--azure-storage-redundancy "LocallyRedundant" '
                 '--currency "USD" '
                 '--discount-percentage 100 '
                 '--percentile "Percentile50" '
                 '--scaling-factor 1.2 '
                 '--sizing-criterion "PerformanceBased" '
                 '--stage "InProgress" '
                 '--time-range "Day" '
                 '--assessment-name "assessment01" '
                 '--group-name "group01" '
                 '--project-name "project01" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az migrate assessments delete '
                 '--assessment-name "assessment01" '
                 '--group-name "group01" '
                 '--project-name "project01" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az migrate assessments get-report-download-url '
                 '--assessment-name "assessment01" '
                 '--group-name "group01" '
                 '--project-name "project01" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az migrate assessed-machines list '
                 '--assessment-name "assessment01" '
                 '--group-name "group01" '
                 '--project-name "project01" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az migrate assessed-machines show '
                 '--assessed-machine-name "amansing_vm1" '
                 '--assessment-name "assessment01" '
                 '--group-name "group01" '
                 '--project-name "project01" '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az migrate operations list',
                 checks=[])
