# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
import json
import filecmp
from pathlib import Path
import shutil

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer,
                               JMESPathCheck, JMESPathCheckExists,
                               NoneCheck)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..')).replace("\\", "/")


class BlueprintScenarioTest(ScenarioTest):
    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_blueprint')
    def test_blueprint(self, resource_group):
        self.kwargs.update({
            'blueprintName': self.create_random_name(prefix='test-bp-', length=24),
            'subscription': self.get_subscription_id(),
            'assignmentName': self.create_random_name(prefix='Assignment-test-bp', length=24),
            'identityName': self.create_random_name(prefix='testid_', length=24),
            'rgName': self.create_random_name(prefix='blueprint-rg-', length=24),
            'policy_filename': TEST_DIR+'/input/create/policy_params.json',
            'blueprint_filename': TEST_DIR+'/input/create/blueprint_params.json'
        })

        test_identity = self.cmd('az identity create '
                                 '-g {rg} '
                                 '-n {identityName}').get_output_in_json()
        self.kwargs.update({
            'userAssignedIdentity': test_identity['id'],
            'identityPrincipalId': test_identity['principalId']
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
            'az blueprint resource-group show '
            '--blueprint-name "{blueprintName}" '
            '--artifact-name "myRgArt" ',
            checks=[
                JMESPathCheck(
                    'myRgArt.displayName',
                    "Resource Group 1")
            ])

        self.cmd(
            'az blueprint resource-group list '
            '--blueprint-name "{blueprintName}" ',
            checks=[
                self.check('length(@)', 1)
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
            '--parameters {policy_filename}',
            checks=[JMESPathCheck('name', 'policy-audit-win-vm-art')])

        self.cmd(
            'blueprint artifact show '
            '--blueprint-name "{blueprintName}" '
            '--name "policy-audit-win-vm-art" ',
            checks=[JMESPathCheck('name', 'policy-audit-win-vm-art')])

        self.cmd(
            'az blueprint show '
            '--name "{blueprintName}" ',
            checks=[JMESPathCheck('name', self.kwargs.get('blueprintName', ''))])

        self.cmd(
            'blueprint update '
            '--name "{blueprintName}" '
            '--parameters {blueprint_filename}',
            checks=[JMESPathCheckExists('parameters')])

        self.cmd(
            'az blueprint publish '
            '--blueprint-name "{blueprintName}" '
            '--version "1.0" '
            '--change-notes "First release"',
            checks=[])

        self.cmd(
            'az blueprint version show '
            '--blueprint-name "{blueprintName}" '
            '--version "1.0" ',
            checks=[])

        self.cmd(
            'az blueprint version list '
            '--blueprint-name "{blueprintName}" ',
            checks=[])

        self.cmd(
            'az blueprint version artifact show '
            '--blueprint-name "{blueprintName}" '
            '--artifact-name "reader-role-art" '
            '--version "1.0" ',
            checks=[])

        self.cmd(
            'az blueprint version artifact list '
            '--blueprint-name "{blueprintName}" '
            '--version "1.0" ',
            checks=[])

        self.cmd(
            'az blueprint version delete '
            '--blueprint-name "{blueprintName}" '
            '--version "1.0" '
            '-y',
            checks=[])

        self.cmd(
            'az blueprint artifact role update '
            '--blueprint-name "{blueprintName}" '
            '--artifact-name "reader-role-art" '
            '--description "Role description." ',
            checks=[JMESPathCheck('description', 'Role description.')])

        self.cmd(
            'az blueprint artifact policy update '
            '--blueprint-name "{blueprintName}" '
            '--artifact-name "policy-audit-win-vm-art" '
            '--description "Policy description."',
            checks=[JMESPathCheck('description', 'Policy description.')])

        self.cmd(
            'az blueprint artifact delete '
            '--blueprint-name "{blueprintName}" '
            '--name "policy-audit-win-vm-art" -y')

        self.cmd(
            'az blueprint resource-group update '
            '--blueprint-name "{blueprintName}" '
            '--artifact-name "myRgArt" '
            '--display-name "Resource Group 2"',
            checks=[
                JMESPathCheck(
                    'myRgArt.displayName',
                    "Resource Group 2")
            ])

        self.cmd(
            'az blueprint resource-group remove '
            '--blueprint-name "{blueprintName}" '
            '--artifact-name "myRgArt" -y ',
            checks=[])

        self.cmd('az blueprint delete '
                 '--name "{blueprintName}" '
                 '-y',
                 checks=[])

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_blueprint_assignment')
    def test_blueprint_assignment(self, resource_group):
        self.kwargs.update({
            'blueprintName': self.create_random_name(prefix='test-bp-', length=24),
            'subscription': self.get_subscription_id(),
            'assignmentName': self.create_random_name(prefix='Assignment-test-bp', length=24),
            'identityName': self.create_random_name(prefix='testid_', length=24),
            'rgName': self.create_random_name(prefix='blueprint-rg-', length=24),
            'policy_filename': TEST_DIR + '/input/create/policy_params.json',
            'blueprint_filename': TEST_DIR + '/input/create/blueprint_params.json',
            'assignment_filename': TEST_DIR + '/input/create/assignment_params.json',
        })

        test_identity = self.cmd('az identity create '
                                 '-g {rg} '
                                 '-n {identityName}').get_output_in_json()
        self.kwargs.update({
            'userAssignedIdentity': test_identity['id'],
            'identityPrincipalId': test_identity['principalId']
        })

        self.cmd(
            'az blueprint create '
            '--name "{blueprintName}" '
            '--description "An example blueprint." '
            '--target-scope "subscription"',
            checks=[
                JMESPathCheck('name', self.kwargs.get('blueprintName', ''))
            ])
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
            'az blueprint update '
            '--name "{blueprintName}" '
            '--parameters {blueprint_filename}',
            checks=[JMESPathCheckExists('parameters')])
        self.cmd(
            'az blueprint publish '
            '--blueprint-name "{blueprintName}" '
            '--version "1.0" '
            '--change-notes "First release"',
            checks=[])
        from unittest import mock
        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            assignment = self.cmd(
                'az blueprint assignment create '
                '--name "{assignmentName}" '
                '--location "westus2" '
                '--identity-type "SystemAssigned" '
                '--blueprint-version "/subscriptions/{subscription}/providers/Microsoft.Blueprint/blueprints/{blueprintName}/versions/1.0" '
                '--locks-mode "None" '
                '--resource-group-value artifact_name=myRgArt name={rgName} location=westus2 '
                '--parameters {assignment_filename}')

        self.cmd(
            'az blueprint assignment wait '
            '--name "{assignmentName}" '
            '--created',
            checks=[])

        self.cmd(
            'az blueprint assignment show '
            '--name "{assignmentName}"',
            checks=[self.check('provisioningState', 'succeeded')])

        self.cmd('az blueprint assignment list ', )

        self.cmd('az blueprint assignment who '
                 '--name "{assignmentName}"')

        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            self.cmd(
                'az role assignment create '
                '--assignee-object-id {identityPrincipalId} '
                '--role Owner '
                '--scope /subscriptions/{subscription}/resourceGroups/{rgName}')

        import time
        time.sleep(600)
        self.cmd(
            'az blueprint assignment update '
            '--name "{assignmentName}" '
            '--location "westus2" '
            '--user-assigned-identity {userAssignedIdentity} '
            '--locks-mode "AllResourcesReadOnly" ',
            checks=[self.exists('identity.userAssignedIdentities'),
                    self.check('locks.mode', 'AllResourcesReadOnly', case_sensitive=False)]).get_output_in_json()

        self.cmd(
            'az blueprint assignment wait '
            '--name "{assignmentName}" '
            '--updated',
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
            'az blueprint resource-group remove '
            '--blueprint-name "{blueprintName}" '
            '--artifact-name "myRgArt" -y ',
            checks=[])

        self.cmd('az blueprint delete '
                 '--name "{blueprintName}" '
                 '-y',
                 checks=[])

        # delete a blueprint assignment will not delete the resources created in the target scope
        # delete the resource group that contains the created resources to clean up
        self.cmd('az group delete '
                 '--subscription "{subscription}" '
                 '--name "{rgName}" '
                 '-y')

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_blueprint_import')
    def test_blueprint_import(self, resource_group):

        self.kwargs.update({
            'blueprintName': self.create_random_name(prefix='test-import-bp', length=24),
            'subscription': self.get_subscription_id(),
            'assignmentName': self.create_random_name(prefix='Assignment-test-import-bp', length=32),
            'input_path_01': TEST_DIR+'/input/import_with_arm',
            'input_path_02': TEST_DIR+'/input/import_with_artifacts',
            'assignment_filename': TEST_DIR+'/input/import_with_artifacts/assignment_params.json',
        })

        self.cmd(
            'az blueprint import '
            '--name "{blueprintName}" '
            '--input-path {input_path_01} '
            '-y',
            checks=[JMESPathCheck('name', self.kwargs.get('blueprintName', '')),
                    JMESPathCheck('targetScope', 'subscription'),
                    JMESPathCheckExists('resourceGroups.storageRG')])

        # this will overwrite the previous settings
        self.cmd(
            'az blueprint import '
            '--name "{blueprintName}" '
            '--input-path {input_path_02} '
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
        from unittest import mock
        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            assignment = self.cmd(
                'az blueprint assignment create '
                '--name "{assignmentName}" '
                '--location "westus2" '
                '--identity-type "SystemAssigned" '
                '--blueprint-version "/subscriptions/{subscription}/providers/Microsoft.Blueprint/blueprints/{blueprintName}/versions/1.0" '
                '--locks-mode "None" '
                '--resource-group-value artifact_name=storageRG name=storage-rg location=westus2 '
                '--parameters {assignment_filename}',
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

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_blueprint_export')
    def test_blueprint_export(self, resource_group):
        # same procedure as testing the import, build a blueprint to export
        self.kwargs.update({
            'blueprintName': self.create_random_name(prefix='test-imported-bp', length=24),
            'subscription': self.get_subscription_id(),
            'input_path': TEST_DIR+'/input/export_with_artifacts/input',
            'output_path': TEST_DIR+'/input/export_with_artifacts/exported',
        })

        # this will overwrite the previous settings
        self.cmd(
            'az blueprint import '
            '--name "{blueprintName}" '
            '--input-path {input_path} '
            '-y',
            checks=[])

        self.cmd(
            'az blueprint export '
            '--output-path {output_path} '
            '--name "{blueprintName}" '
            '--yes',
            checks=[])

        # check if the import and output artifacts are equal in content
        input_blueprint = TEST_DIR + "/input/export_with_artifacts/input/blueprint.json"
        input_artifact_directory = TEST_DIR + "/input/export_with_artifacts/input/artifacts"
        output_blueprint = TEST_DIR + f"/input/export_with_artifacts/exported/{self.kwargs['blueprintName']}/blueprint.json"
        output_artifact_directory = TEST_DIR + f"/input/export_with_artifacts/exported/{self.kwargs['blueprintName']}/artifacts"
        output_path = Path(f"/input/export_with_artifacts/exported/{self.kwargs['blueprintName']}")
        # recursive function to check for json equality
        def ordered(obj):
            if isinstance(obj, dict):
                return sorted((k, ordered(v)) for k, v in obj.items())
            if isinstance(obj, list):
                return sorted(ordered(x) for x in obj)
            else:
                return obj

        # file comparison
        with open(input_blueprint) as input_f:
            input_blueprint = json.load(input_f)
            ordered_input_blueprint = ordered(input_blueprint)
        with open(output_blueprint) as output_f:
            output_blueprint = json.load(output_f)
            ordered_output_blueprint = ordered(output_blueprint)

        try:
            self.assertEqual(ordered_input_blueprint, ordered_output_blueprint)
        except AssertionError:
            if output_path.exists() and output_path.is_dir():
                shutil.rmtree(output_path)
            raise

        # artifact directory comparison
        artifacts_cmp = filecmp.dircmp(input_artifact_directory, output_artifact_directory)
        try:
            assert len(artifacts_cmp.right_only) == 0 and len(artifacts_cmp.left_only) == 0 and len(artifacts_cmp.funny_files) == 0
        except AssertionError:
            if output_path.exists() and output_path.is_dir():
                shutil.rmtree(output_path)
            raise

        # artifact file comparison
        for filename in os.listdir(input_artifact_directory):
            with open(os.path.join(input_artifact_directory, filename)) as input_f:
                input_artifact = json.load(input_f)
                ordered_input_artifact = ordered(input_artifact)
            with open(os.path.join(output_artifact_directory, filename)) as output_f:
                output_artifact = json.load(output_f)
                ordered_output_artifact = ordered(output_artifact)
            try:
                self.assertEqual(ordered_input_artifact, ordered_output_artifact)
            except AssertionError:
                if output_path.exists() and output_path.is_dir():
                    shutil.rmtree(output_path)
                raise

        self.cmd('az blueprint delete '
                 '--name "{blueprintName}" '
                 '-y',
                 checks=[JMESPathCheck('name', self.kwargs.get('blueprintName', ''))])

        if output_path.exists() and output_path.is_dir():
            shutil.rmtree(output_path)
