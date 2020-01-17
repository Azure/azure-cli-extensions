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
            'blueprintName': 'test-bp',
            # 'managementGroupId': 'CliMgmtGroup',
            # 'subId': '0b1f6471-1bf0-4dda-aec3-cb9272f09590',
            'scope': 'subscriptions/0b1f6471-1bf0-4dda-aec3-cb9272f09590'
        })

        self.cmd('az blueprint create '
                 '--scope "{scope}" '
                 '--name "{blueprintName}" '
                 '--description "An example blueprint." '
                 '--target-scope "subscription"',
                 checks=[])

        self.cmd('az blueprint list '
                 '--scope "{scope}"',
                 checks=[])

        self.cmd('az blueprint resource-group create '
                 '--scope "{scope}" '
                 '--blueprint-name "{blueprintName}" '
                 '--artifact-name "my-rg-art" '
                 '--target-scope "subscription"',
                 checks=[])

        self.cmd('az blueprint artifact role create '
                 '--scope "{scope}" '
                 '--blueprint-name "{blueprintName}" '
                 '--artifact-name "reader-role-art" '
                 '--role-definition-id "/providers/Microsoft.Authorization/roleDefinitions/acdd72a7-3385-48ef-bd42-f606fba81ae7" '
                 '--principal-ids "[parameters(\'[Usergrouporapplicationname]:Reader_RoleAssignmentName\')]" '
                 '--parameters "{\:q"RoleAssignmentName\":{\"value\":\"[parameters(\'[Usergrouporapplicationname]:Reader_RoleAssignmentName\')]\"}}}}"',
                 checks=[])
 

        self.cmd('az blueprint published create '
                 '--scope "{scope}" '
                 '--blueprint-name "{blueprintName}" '
                 '--version "1.0" '
                 '--change-notes "First release"',
                 checks=[])

        self.cmd('az blueprint published delete '
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
