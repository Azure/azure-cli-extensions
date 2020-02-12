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
            'scope': 'subscriptions/00000000-0000-0000-0000-000000000000',
            'subscription': '00000000-0000-0000-0000-000000000000',
            'assignmentName': 'Assignment-test-bp'
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
                 '--artifact-name "my-rg-art"',
                 checks=[])

        self.cmd('az blueprint artifact role create '
                 '--scope "{scope}" '
                 '--blueprint-name "{blueprintName}" '
                 '--artifact-name "reader-role-art" '
                 '--display-name "[User group or application name] : Reader" '
                 '--resource-group-art "my-rg-art" '
                 '--role-definition-id "/providers/Microsoft.Authorization/roleDefinitions/acdd72a7-3385-48ef-bd42-f606fba81ae7" '
                 r'''--principal-ids "[parameters('[Usergrouporapplicationname]:Reader_RoleAssignmentName')]"''',
                 checks=[])

        self.cmd('az blueprint artifact policy create '
                 '--scope "{scope}" '
                 '--blueprint-name "{blueprintName}" '
                 '--artifact-name "policy-audit-win-vm-art" '
                 '--display-name "Audit Windows VMs in which the Administrators group does not contain only the specified members" '
                 '--policy-definition-id "/providers/Microsoft.Authorization/policySetDefinitions/06122b01-688c-42a8-af2e-fa97dd39aa3b" '
                 '--resource-group-art "my-rg-art" '
                 '--parameters @src/blueprint/azext_blueprint/tests/latest/input/create/policy_params.json',
                 checks=[])

        self.cmd('az blueprint update '
                 '--scope "{scope}" '
                 '--name "{blueprintName}" '
                 '--parameters @src/blueprint/azext_blueprint/tests/latest/input/create/blueprint_params.json',
                 checks=[])

        self.cmd('az blueprint published create '
                 '--scope "{scope}" '
                 '--blueprint-name "{blueprintName}" '
                 '--version "1.0" '
                 '--change-notes "First release"',
                 checks=[])

        self.cmd('az blueprint assignment create '
                 '--scope "{scope}" '
                 '--assignment-name "{assignmentName}" '
                 '--location "westus2" '
                 '--identity-type "SystemAssigned" '
                 '--blueprint-id "/subscriptions/0b1f6471-1bf0-4dda-aec3-cb9272f09590/providers/Microsoft.Blueprint/blueprints/test-bp/versions/1.0" '
                 '--locks-mode "None" '
                 '--resource-groups @src/blueprint/azext_blueprint/tests/latest/input/create/resource_group_params.json '
                 '--parameters @src/blueprint/azext_blueprint/tests/latest/input/create/assignment_params.json',
                 checks=[])

        self.cmd('az blueprint assignment wait '
                 '--scope "{scope}" '
                 '--assignment-name "{assignmentName}" '
                 '''--custom "provisioningState=='succeeded'" '''
                 '--created',
                 checks=[])

        self.cmd('az blueprint assignment show '
                 '--scope "{scope}" '
                 '--assignment-name "{assignmentName}"',
                 checks=[])

        self.cmd('az blueprint assignment delete '
                 '--scope "{scope}" '
                 '--assignment-name "{assignmentName}" '
                 '-y',
                 checks=[])

        self.cmd('az blueprint assignment wait '
                 '--scope "{scope}" '
                 '--assignment-name "{assignmentName}" '
                 '''--custom "provisioningState=='succeeded'" '''
                 '--deleted',
                 checks=[])

        self.cmd('az blueprint published delete '
                 '--scope "{scope}" '
                 '--blueprint-name "{blueprintName}" '
                 '--version "1.0" '
                 '-y',
                 checks=[])

        self.cmd('az blueprint delete '
                 '--scope "{scope}" '
                 '--name "{blueprintName}" '
                 '-y',
                 checks=[])

        # delete a blueprint assignment will not delete the resources created in the target scope
        # delete the resource group that contains the created resources to clean up
        self.cmd('az group delete '
                 '--subscription "{subscription}" '
                 '--name "blueprint-rg" '
                 '-y')
