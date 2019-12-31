# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class BlueprintScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_blueprint')
    def test_blueprint(self, resource_group):

        self.kwargs.update({
            'name': 'test1',
            'ManagementGroupId': 'CliMgmtGroup',
            'subId':'0b1f6471-1bf0-4dda-aec3-cb9272f09590'
        })

        self.cmd('az blueprint list '
                 '--scope "subscriptions/{subId}"',
                 checks=[])

        self.cmd('az blueprint create '
                 '--scope "providers/Microsoft.Management/managementGroups/{ManagementGroupId}" '
                 '--name "simpleBlueprint" '
                 '--description "An example blueprint containing an RG with two tags." '
                 '--target-scope "subscription"',
                 checks=[])

        self.cmd('az blueprint list '
                 '--scope "providers/Microsoft.Management/managementGroups/{ManagementGroupId}"',
                 checks=[])

        self.cmd('az blueprint assign create '
                 '--scope "subscriptions/{subId}}" '
                 '--name "assignSimpleBlueprint" '
                 '--location "eastus" '
                 '--identity-type "SystemAssigned" '
                 '--description "enforce pre-defined simpleBlueprint to this XXXXXXXX subscription." '
                 '--blueprint-id "/providers/Microsoft.Management/managementGroups/ContosoOnlineGroup/providers/Microsoft.Blueprint/blueprints/simpleBlueprint"',
                 checks=[])

        self.cmd('az blueprint create '
                 '--scope "subscriptions/00000000-0000-0000-0000-000000000000" '
                 '--name "assignSimpleBlueprint" '
                 '--location "eastus" '
                 '--identity-type "UserAssigned" '
                 '--description "enforce pre-defined simpleBlueprint to this XXXXXXXX subscription." '
                 '--blueprint-id "/providers/Microsoft.Management/managementGroups/ContosoOnlineGroup/providers/Microsoft.Blueprint/blueprints/simpleBlueprint"',
                 checks=[])

        self.cmd('az blueprint published create '
                 '--scope "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" '
                 '--name "simpleBlueprint" '
                 '--version-id "v2"',
                 checks=[])

        self.cmd('az blueprint published create '
                 '--scope "subscriptions/00000000-0000-0000-0000-000000000000" '
                 '--name "simpleBlueprint" '
                 '--version-id "v2"',
                 checks=[])

        self.cmd('az blueprint artifact delete '
                 '--scope "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" '
                 '--blueprint-name "simpleBlueprint" '
                 '--name "ownerAssignment"',
                 checks=[])

        self.cmd('az blueprint artifact delete '
                 '--scope "subscriptions/00000000-0000-0000-0000-000000000000" '
                 '--blueprint-name "simpleBlueprint" '
                 '--name "storageTemplate"',
                 checks=[])

        self.cmd('az blueprint artifact delete '
                 '--scope "subscriptions/00000000-0000-0000-0000-000000000000" '
                 '--blueprint-name "simpleBlueprint" '
                 '--name "costCenterPolicy"',
                 checks=[])

        self.cmd('az blueprint artifact delete '
                 '--scope "subscriptions/00000000-0000-0000-0000-000000000000" '
                 '--blueprint-name "simpleBlueprint" '
                 '--name "ownerAssignment"',
                 checks=[])

        self.cmd('az blueprint artifact delete '
                 '--scope "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" '
                 '--blueprint-name "simpleBlueprint" '
                 '--name "storageTemplate"',
                 checks=[])

        self.cmd('az blueprint artifact delete '
                 '--scope "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" '
                 '--blueprint-name "simpleBlueprint" '
                 '--name "costCenterPolicy"',
                 checks=[])

        self.cmd('az blueprint list '
                 '--scope "subscriptions/00000000-0000-0000-0000-000000000000"',
                 checks=[])

        self.cmd('az blueprint artifact delete '
                 '--scope "subscriptions/00000000-0000-0000-0000-000000000000" '
                 '--blueprint-name "simpleBlueprint" '
                 '--name "storageTemplate"',
                 checks=[])

        self.cmd('az blueprint artifact delete '
                 '--scope "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" '
                 '--blueprint-name "simpleBlueprint" '
                 '--name "ownerAssignment"',
                 checks=[])

        self.cmd('az blueprint artifact delete '
                 '--scope "subscriptions/00000000-0000-0000-0000-000000000000" '
                 '--blueprint-name "simpleBlueprint" '
                 '--name "costCenterPolicy"',
                 checks=[])

        self.cmd('az blueprint artifact delete '
                 '--scope "subscriptions/00000000-0000-0000-0000-000000000000" '
                 '--blueprint-name "simpleBlueprint" '
                 '--name "ownerAssignment"',
                 checks=[])

        self.cmd('az blueprint artifact delete '
                 '--scope "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" '
                 '--blueprint-name "simpleBlueprint" '
                 '--name "storageTemplate"',
                 checks=[])

        self.cmd('az blueprint artifact delete '
                 '--scope "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" '
                 '--blueprint-name "simpleBlueprint" '
                 '--name "costCenterPolicy"',
                 checks=[])

        self.cmd('az blueprint list '
                 '--scope "subscriptions/00000000-0000-0000-0000-000000000000"',
                 checks=[])

        self.cmd('az blueprint artifact list '
                 '--scope "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" '
                 '--blueprint-name "simpleBlueprint"',
                 checks=[])

        self.cmd('az blueprint artifact list '
                 '--scope "subscriptions/00000000-0000-0000-0000-000000000000" '
                 '--blueprint-name "simpleBlueprint"',
                 checks=[])

        self.cmd('az blueprint artifact delete '
                 '--scope "subscriptions/00000000-0000-0000-0000-000000000000" '
                 '--blueprint-name "simpleBlueprint" '
                 '--name "ownerAssignment"',
                 checks=[])

        self.cmd('az blueprint artifact delete '
                 '--scope "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" '
                 '--blueprint-name "simpleBlueprint" '
                 '--name "storageTemplate"',
                 checks=[])

        self.cmd('az blueprint artifact delete '
                 '--scope "subscriptions/00000000-0000-0000-0000-000000000000" '
                 '--blueprint-name "simpleBlueprint" '
                 '--name "storageTemplate"',
                 checks=[])

        self.cmd('az blueprint artifact delete '
                 '--scope "subscriptions/00000000-0000-0000-0000-000000000000" '
                 '--blueprint-name "simpleBlueprint" '
                 '--name "costCenterPolicy"',
                 checks=[])

        self.cmd('az blueprint artifact delete '
                 '--scope "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" '
                 '--blueprint-name "simpleBlueprint" '
                 '--name "costCenterPolicy"',
                 checks=[])

        self.cmd('az blueprint artifact delete '
                 '--scope "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" '
                 '--blueprint-name "simpleBlueprint" '
                 '--name "ownerAssignment"',
                 checks=[])

        self.cmd('az blueprint published list '
                 '--scope "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" '
                 '--name "simpleBlueprint"',
                 checks=[])

        self.cmd('az blueprint published list '
                 '--scope "subscriptions/00000000-0000-0000-0000-000000000000" '
                 '--name "simpleBlueprint"',
                 checks=[])

        self.cmd('az blueprint list '
                 '--scope "subscriptions/00000000-0000-0000-0000-000000000000"',
                 checks=[])

        self.cmd('az blueprint artifact list '
                 '--scope "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" '
                 '--blueprint-name "simpleBlueprint"',
                 checks=[])

        self.cmd('az blueprint artifact list '
                 '--scope "subscriptions/00000000-0000-0000-0000-000000000000" '
                 '--blueprint-name "simpleBlueprint"',
                 checks=[])

        self.cmd('az blueprint published list '
                 '--scope "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" '
                 '--name "simpleBlueprint"',
                 checks=[])

        self.cmd('az blueprint published list '
                 '--scope "subscriptions/00000000-0000-0000-0000-000000000000" '
                 '--name "simpleBlueprint"',
                 checks=[])

        self.cmd('az blueprint list '
                 '--scope "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup"',
                 checks=[])

        self.cmd('az blueprint list '
                 '--scope "subscriptions/00000000-0000-0000-0000-000000000000"',
                 checks=[])

        self.cmd('az blueprint list '
                 '--scope "subscriptions/00000000-0000-0000-0000-000000000000"',
                 checks=[])

        self.cmd('az blueprint list '
                 '--scope "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup"',
                 checks=[])

        self.cmd('az blueprint list '
                 '--scope "subscriptions/00000000-0000-0000-0000-000000000000"',
                 checks=[])

        self.cmd('az blueprint who_is_blueprint '
                 '--scope "subscriptions/00000000-0000-0000-0000-000000000000" '
                 '--name "assignSimpleBlueprint"',
                 checks=[])

        self.cmd('az blueprint artifact delete '
                 '--scope "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" '
                 '--blueprint-name "simpleBlueprint" '
                 '--name "ownerAssignment"',
                 checks=[])

        self.cmd('az blueprint artifact delete '
                 '--scope "subscriptions/00000000-0000-0000-0000-000000000000" '
                 '--blueprint-name "simpleBlueprint" '
                 '--name "storageTemplate"',
                 checks=[])

        self.cmd('az blueprint artifact delete '
                 '--scope "subscriptions/00000000-0000-0000-0000-000000000000" '
                 '--blueprint-name "simpleBlueprint" '
                 '--name "costCenterPolicy"',
                 checks=[])

        self.cmd('az blueprint artifact delete '
                 '--scope "subscriptions/00000000-0000-0000-0000-000000000000" '
                 '--blueprint-name "simpleBlueprint" '
                 '--name "ownerAssignment"',
                 checks=[])

        self.cmd('az blueprint artifact delete '
                 '--scope "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" '
                 '--blueprint-name "simpleBlueprint" '
                 '--name "storageTemplate"',
                 checks=[])

        self.cmd('az blueprint artifact delete '
                 '--scope "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" '
                 '--blueprint-name "simpleBlueprint" '
                 '--name "costCenterPolicy"',
                 checks=[])

        self.cmd('az blueprint published list '
                 '--scope "subscriptions/00000000-0000-0000-0000-000000000000" '
                 '--name "simpleBlueprint"',
                 checks=[])

        self.cmd('az blueprint published list '
                 '--scope "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup" '
                 '--name "simpleBlueprint"',
                 checks=[])

        self.cmd('az blueprint delete '
                 '--scope "subscriptions/00000000-0000-0000-0000-000000000000" '
                 '--name "assignSimpleBlueprint"',
                 checks=[])

        self.cmd('az blueprint list '
                 '--scope "providers/Microsoft.Management/managementGroups/ContosoOnlineGroup"',
                 checks=[])

        self.cmd('az blueprint list '
                 '--scope "subscriptions/00000000-0000-0000-0000-000000000000"',
                 checks=[])
