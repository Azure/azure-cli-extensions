# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer,
                               JMESPathCheck, JMESPathCheckExists,
                               NoneCheck)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class BlueprintScenarioTest(ScenarioTest):
    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_blueprint')
    def test_blueprint(self, resource_group):

        self.kwargs.update({
            'blueprintName': 'test-bp',
            'subscription': '00000000-0000-0000-0000-000000000000',
            'assignmentName': 'Assignment-test-bp'
        })

        self.cmd(
            'az blueprint create '
            '--name "{blueprintName}" '
            '--description "An example blueprint." '
            '--target-scope "subscription"',
            checks=[
                JMESPathCheck('name', self.kwargs.get('blueprintName', ''))
            ])

        self.cmd('az blueprint list', checks=[])

        self.cmd(
            'az blueprint resource-group add '
            '--blueprint-name "{blueprintName}" '
            '--artifact-name "myRgArt" '
            '--display-name "Resource Group 1"',
            checks=[
                JMESPathCheck(
                    'myRgArt.displayName',
                    "Resource Group 1")
            ])

        self.cmd(
            'az blueprint artifact role create '
            '--blueprint-name "{blueprintName}" '
            '--artifact-name "reader-role-art" '
            '--display-name "[User group or application name] : Reader" '
            '--resource-group-art "myRgArt" '
            '--role-definition-id "/providers/Microsoft.Authorization/roleDefinitions/acdd72a7-3385-48ef-bd42-f606fba81ae7" '
            '''--principal-ids "[parameters('reader')]"''',
            checks=[JMESPathCheck('name', 'reader-role-art')])

        self.cmd(
            'az blueprint artifact policy create '
            '--blueprint-name "{blueprintName}" '
            '--artifact-name "policy-audit-win-vm-art" '
            '--display-name "Audit Windows VMs in which the Administrators group does not contain only the specified members" '
            '--policy-definition-id "/providers/Microsoft.Authorization/policySetDefinitions/06122b01-688c-42a8-af2e-fa97dd39aa3b" '
            '--resource-group-art "myRgArt" '
            '--parameters @src/blueprint/azext_blueprint/tests/latest/input/create/policy_params.json',
            checks=[JMESPathCheck('name', 'policy-audit-win-vm-art')])

        self.cmd(
            'az blueprint update '
            '--name "{blueprintName}" '
            '--parameters @src/blueprint/azext_blueprint/tests/latest/input/create/blueprint_params.json',
            checks=[JMESPathCheckExists('parameters')])

        self.cmd(
            'az blueprint publish '
            '--blueprint-name "{blueprintName}" '
            '--version "1.0" '
            '--change-notes "First release"',
            checks=[])

        assignment = self.cmd(
            'az blueprint assignment create '
            '--name "{assignmentName}" '
            '--location "westus2" '
            '--identity-type "SystemAssigned" '
            '--blueprint-version "/subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.Blueprint/blueprints/{blueprintName}/versions/1.0" '
            '--locks-mode "None" '
            '--resource-group-value artifact_name=myRgArt name=blueprint-rg location=westus2 '
            '--parameters @src/blueprint/azext_blueprint/tests/latest/input/create/assignment_params.json',
            checks=[JMESPathCheckExists('identity.principalId')]).get_output_in_json()

        principal_id = assignment['identity']['principalId']
        assert len(principal_id) > 0

        self.cmd(
            'az blueprint assignment wait '
            '--name "{assignmentName}" '
            '--created',
            checks=[])

        self.cmd(
            'az blueprint assignment show '
            '--name "{assignmentName}"',
            checks=[])

        self.cmd(
            'az blueprint assignment delete '
            '--name "{assignmentName}" '
            '-y',
            checks=[])

        self.cmd(
            'az blueprint assignment wait '
            '--name "{assignmentName}" '
            '--deleted',
            checks=[])

        self.cmd(
            'az blueprint version delete '
            '--blueprint-name "{blueprintName}" '
            '--version "1.0" '
            '-y',
            checks=[])

        self.cmd('az blueprint delete '
                 '--name "{blueprintName}" '
                 '-y',
                 checks=[])

        # delete a blueprint assignment will not delete the resources created in the target scope
        # delete the resource group that contains the created resources to clean up
        self.cmd('az group delete '
                 '--subscription "{subscription}" '
                 '--name "blueprint-rg" '
                 '-y')

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_blueprint_import')
    def test_blueprint_import(self, resource_group):

        self.kwargs.update({
            'blueprintName': 'test-import-bp',
            'subscription': '00000000-0000-0000-0000-000000000000',
            'assignmentName': 'Assignment-test-import-bp'
        })

        self.cmd(
            'az blueprint import '
            '--name "{blueprintName}" '
            '--input-path "src/blueprint/azext_blueprint/tests/latest/input/import_with_arm" '
            '-y',
            checks=[JMESPathCheck('name', self.kwargs.get('blueprintName', '')),
                    JMESPathCheck('targetScope', 'subscription'),
                    JMESPathCheckExists('resourceGroups.storageRG')])

        # this will overwrite the previous settings
        self.cmd(
            'az blueprint import '
            '--name "{blueprintName}" '
            '--input-path "src/blueprint/azext_blueprint/tests/latest/input/import_with_artifacts" '
            '-y',
            checks=[JMESPathCheckExists('parameters.contributors')])

        self.cmd(
            'az blueprint artifact list '
            '--blueprint-name "{blueprintName}" ',
            checks=[
                JMESPathCheckExists('[3].kind'),
                JMESPathCheck('[3].kind', 'roleAssignment')
            ])

        self.cmd(
            'az blueprint publish '
            '--blueprint-name "{blueprintName}" '
            '--version "1.0" '
            '--change-notes "First release"',
            checks=[JMESPathCheck('name', '1.0')])

        assignment = self.cmd(
            'az blueprint assignment create '
            '--name "{assignmentName}" '
            '--location "westus2" '
            '--identity-type "SystemAssigned" '
            '--blueprint-version "/subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.Blueprint/blueprints/{blueprintName}/versions/1.0" '
            '--locks-mode "None" '
            '--resource-group-value artifact_name=storageRG name=storage-rg location=westus2 '
            '--parameters @src/blueprint/azext_blueprint/tests/latest/input/import_with_artifacts/assignment_params.json',
            checks=[JMESPathCheckExists('identity.principalId')]).get_output_in_json()

        principal_id = assignment['identity']['principalId']
        assert len(principal_id) > 0

        # Sometimes automatic role assignment by blueprint fails, we may need the following.
        # Assign owner of target subscription to the service principal created by blueprint assignment
        # self.cmd(
        #     'az role assignment create '
        #     '--role owner '
        #     '--assignee-object-id {} '
        #     '--scope "/subscriptions/{}" '
        #     '--assignee-principal-type ServicePrincipal '
        #     '-g='.format(principal_id, self.kwargs.get('subscription', '')),
        #     checks=[JMESPathCheck('principalId', principal_id)]
        # )

        self.cmd(
            'az blueprint assignment wait '
            '--name "{assignmentName}" '
            '--created',
            checks=[])

        # remove owner role after resources created
        # self.cmd(
        #     'az role assignment delete '
        #     '--role owner '
        #     '--assignee {} '
        #     '--scope "/subscriptions/{}" '
        #     '-g='.format(principal_id, self.kwargs.get('subscription', '')),
        #     self.checks=[]
        # )

        self.cmd(
            'az blueprint assignment show '
            '--name "{assignmentName}"',
            checks=[])

        self.cmd(
            'az blueprint assignment delete '
            '--name "{assignmentName}" '
            '-y',
            checks=[])

        self.cmd(
            'az blueprint assignment wait '
            '--name "{assignmentName}" '
            '--deleted',
            checks=[])

        self.cmd(
            'az blueprint version delete '
            '--blueprint-name "{blueprintName}" '
            '--version "1.0" '
            '-y',
            checks=[JMESPathCheck('name', '1.0')])

        self.cmd('az blueprint delete '
                 '--name "{blueprintName}" '
                 '-y',
                 checks=[JMESPathCheck('name', self.kwargs.get('blueprintName', ''))])

        self.cmd('az group delete '
                 '--subscription "{subscription}" '
                 '--name "storage-rg" '
                 '-y')
