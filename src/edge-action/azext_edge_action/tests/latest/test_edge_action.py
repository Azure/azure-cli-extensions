# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import base64
from io import BytesIO
import os
from unittest.mock import patch
import zipfile
from azure.cli.testsdk import ResourceGroupPreparer, JMESPathCheck, ScenarioTest

from .recording_processors import EdgeActionRecordingProcessor

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


def _patch_playback_polling(test):
    patcher = patch('azure.cli.core.aaz._poller.AAZBasePolling._delay', return_value=None)
    patcher.start()
    test.addCleanup(patcher.stop)


class EdgeActionScenarioTest(ScenarioTest):

    def __init__(self, method_name):
        super().__init__(
            method_name,
            recording_processors=[EdgeActionRecordingProcessor()],
            replay_processors=[EdgeActionRecordingProcessor()],
            replay_patches=[_patch_playback_polling],
        )
        self.vcr.match_on = (*self.vcr.match_on, 'body')

    @ResourceGroupPreparer(name_prefix='clitests', location='eastus', additional_tags={'owner': 'edgeaction'})
    def test_edge_action_crud(self, resource_group):
        """Test Edge Action CRUD operations"""
        edge_action_name = self.create_random_name(prefix='edgeaction', length=20)

        # Test list edge actions (should be empty initially)
        list_checks = [JMESPathCheck('length(@)', 0)]
        self.cmd('edge-action list -g {}'.format(resource_group), checks=list_checks)

        # Test create edge action
        create_checks = [
            JMESPathCheck('name', edge_action_name),
            JMESPathCheck('resourceGroup', resource_group),
            JMESPathCheck('location', 'global'),
            JMESPathCheck('provisioningState', 'Succeeded'),
            JMESPathCheck('sku.name', 'Standard'),
            JMESPathCheck('sku.tier', 'Standard'),
        ]
        created = self.cmd('edge-action create -g {} -n {} --sku name=Standard tier=Standard --location global'.format(
            resource_group, edge_action_name), checks=create_checks).get_output_in_json()

        self.cmd('edge-action list', checks=[
            JMESPathCheck("contains([].id, '{}')".format(created['id']), True),
        ])

        # Test show edge action
        self.cmd('edge-action show -g {} -n {}'.format(resource_group, edge_action_name), checks=create_checks)

        # Test list edge actions (should contain 1 item now)
        list_checks = [JMESPathCheck('length(@)', 1)]
        self.cmd('edge-action list -g {}'.format(resource_group), checks=list_checks)

        # Test update edge action
        for tags, expected in [('test=value', {'test': 'value'}), ('"{{}}"', {})]:
            update_checks = create_checks + [JMESPathCheck('tags', expected)]
            self.cmd('edge-action update -g {} -n {} --sku name=Standard tier=Standard --tags {}'.format(
                resource_group, edge_action_name, tags), checks=update_checks)
            self.cmd('edge-action show -g {} -n {}'.format(
                resource_group, edge_action_name), checks=update_checks)

        # Test delete edge action
        self.cmd('edge-action delete -g {} -n {} -y'.format(resource_group, edge_action_name))

        # Verify deletion - list should be empty again
        list_checks = [JMESPathCheck('length(@)', 0)]
        self.cmd('edge-action list -g {}'.format(resource_group), checks=list_checks)

    @ResourceGroupPreparer(additional_tags={'owner': 'edgeaction'})
    def test_edge_action_version_operations(self, resource_group):
        """Test Edge Action Version operations"""
        edge_action_name = self.create_random_name(prefix='edgeaction', length=20)
        version_name = 'v1'

        # Create edge action first
        self.cmd('edge-action create -g {} -n {} --sku name=Standard tier=Standard --location global'.format(
            resource_group, edge_action_name))

        # Test create version
        # The service makes the first version default even when False is requested.
        create_version_checks = [
            JMESPathCheck('name', version_name),
            JMESPathCheck('deploymentType', 'file'),
            JMESPathCheck('isDefaultVersion', 'True'),
            JMESPathCheck('provisioningState', 'Succeeded'),
        ]
        self.cmd('edge-action version create -g {} --edge-action-name {} -n {} --deployment-type file --location global --is-default-version False'.format(
            resource_group, edge_action_name, version_name), checks=create_version_checks)

        # Test show version
        self.cmd('edge-action version show -g {} --edge-action-name {} -n {}'.format(
            resource_group, edge_action_name, version_name), checks=create_version_checks)

        for tags, expected in [('purpose=updated', {'purpose': 'updated'}), ('"{{}}"', {})]:
            update_checks = create_version_checks + [JMESPathCheck('tags', expected)]
            self.cmd('edge-action version update -g {} --edge-action-name {} -n {} --tags {}'.format(
                resource_group, edge_action_name, version_name, tags), checks=update_checks)
            self.cmd('edge-action version show -g {} --edge-action-name {} -n {}'.format(
                resource_group, edge_action_name, version_name), checks=update_checks)

        # Test list versions
        list_version_checks = [JMESPathCheck('length(@)', 1)]
        self.cmd('edge-action version list -g {} --edge-action-name {}'.format(
            resource_group, edge_action_name), checks=list_version_checks)

        # Test delete version
        self.cmd('edge-action version delete -g {} --edge-action-name {} -n {} -y'.format(
            resource_group, edge_action_name, version_name))

        # Clean up edge action
        self.cmd('edge-action delete -g {} -n {} -y'.format(resource_group, edge_action_name))

    @ResourceGroupPreparer(additional_tags={'owner': 'edgeaction'})
    def test_edge_action_version_deploy_with_file(self, resource_group):
        """Test Edge Action Version deployment with file path using custom command"""
        edge_action_name = self.create_random_name(prefix='edgeaction', length=20)
        version_name = 'v1'

        # Create edge action and version
        self.cmd('edge-action create -g {} -n {} --sku name=Standard tier=Standard --location global'.format(
            resource_group, edge_action_name))
        self.cmd('edge-action version create -g {} --edge-action-name {} -n {} --deployment-type file --location global --is-default-version False'.format(
            resource_group, edge_action_name, version_name))

        # Use test fixture file
        test_file = os.path.join(TEST_DIR, 'test_files', 'sample_edge_action.js')

        # Test deploy with file path using custom deploy-from-file command (file mode)
        self.cmd('edge-action version deploy-from-file -g {} --edge-action-name {} --version {} --file-path "{}" --deployment-type file'.format(
            resource_group, edge_action_name, version_name, test_file), checks=[
                JMESPathCheck('name', version_name),
                JMESPathCheck('deploymentType', 'file'),
                JMESPathCheck('provisioningState', 'Succeeded'),
                JMESPathCheck('validationStatus', 'Succeeded'),
        ])

        # Clean up
        self.cmd('edge-action version delete -g {} --edge-action-name {} -n {} -y'.format(
            resource_group, edge_action_name, version_name))
        self.cmd('edge-action delete -g {} -n {} -y'.format(resource_group, edge_action_name))

    @ResourceGroupPreparer(additional_tags={'owner': 'edgeaction'})
    def test_edge_action_version_deploy_with_zip(self, resource_group):
        """Test Edge Action Version deployment with zip file using custom command"""
        edge_action_name = self.create_random_name(prefix='edgeaction', length=20)
        version_name = 'v1'

        # Create edge action and version
        self.cmd('edge-action create -g {} -n {} --sku name=Standard tier=Standard --location global'.format(
            resource_group, edge_action_name))
        self.cmd('edge-action version create -g {} --edge-action-name {} -n {} --deployment-type zip --location global --is-default-version False'.format(
            resource_group, edge_action_name, version_name))

        # Use test fixture zip file
        test_zip = os.path.join(TEST_DIR, 'test_files', 'sample_edge_action.zip')

        # Test deploy with zip file path using custom deploy-from-file command (auto-detects zip)
        self.cmd('edge-action version deploy-from-file -g {} --edge-action-name {} --version {} --file-path "{}"'.format(
            resource_group, edge_action_name, version_name, test_zip), checks=[
                JMESPathCheck('name', version_name),
                JMESPathCheck('deploymentType', 'zip'),
                JMESPathCheck('provisioningState', 'Succeeded'),
                JMESPathCheck('validationStatus', 'Succeeded'),
        ])

        # Clean up
        self.cmd('edge-action version delete -g {} --edge-action-name {} -n {} -y'.format(
            resource_group, edge_action_name, version_name))
        self.cmd('edge-action delete -g {} -n {} -y'.format(resource_group, edge_action_name))

    @ResourceGroupPreparer(additional_tags={'owner': 'edgeaction'})
    def test_edge_action_version_deploy_with_content(self, resource_group):
        """Test Edge Action Version deployment with base64 content (backward compatibility)"""
        edge_action_name = self.create_random_name(prefix='edgeaction', length=20)
        version_name = 'v1'

        # Create edge action and version
        self.cmd('edge-action create -g {} -n {} --sku name=Standard tier=Standard --location global'.format(
            resource_group, edge_action_name))
        self.cmd('edge-action version create -g {} --edge-action-name {} -n {} --deployment-type file --location global --is-default-version False'.format(
            resource_group, edge_action_name, version_name))

        # Test deploy with base64 content
        test_content = base64.b64encode(b'function handler(event) { return event; }').decode('utf-8')
        self.cmd('edge-action version deploy-version-code -g {} --edge-action-name {} --version {} --name testcode --content "{}"'.format(
            resource_group, edge_action_name, version_name, test_content), checks=[
                JMESPathCheck('name', version_name),
                JMESPathCheck('deploymentType', 'file'),
                JMESPathCheck('provisioningState', 'Succeeded'),
                JMESPathCheck('validationStatus', 'Succeeded'),
        ])

        # Clean up
        self.cmd('edge-action version delete -g {} --edge-action-name {} -n {} -y'.format(
            resource_group, edge_action_name, version_name))
        self.cmd('edge-action delete -g {} -n {} -y'.format(resource_group, edge_action_name))

    @ResourceGroupPreparer(additional_tags={'owner': 'edgeaction'})
    def test_edge_action_version_get_version_code(self, resource_group):
        """Test Edge Action Version get-version-code command"""
        edge_action_name = self.create_random_name(prefix='edgeaction', length=20)
        version_name = 'v1'

        # Create edge action and version
        self.cmd('edge-action create -g {} -n {} --sku name=Standard tier=Standard --location global'.format(
            resource_group, edge_action_name))
        self.cmd('edge-action version create -g {} --edge-action-name {} -n {} --deployment-type file --location global --is-default-version False'.format(
            resource_group, edge_action_name, version_name))

        # Deploy version code
        test_content = base64.b64encode(b'function handler(event) { return event; }').decode('utf-8')
        self.cmd('edge-action version deploy-version-code -g {} --edge-action-name {} --version {} --name testcode --content "{}"'.format(
            resource_group, edge_action_name, version_name, test_content))

        # Test get-version-code command (this tests the fix for Unsupported Media Type error)
        result = self.cmd('edge-action version get-version-code -g {} --edge-action-name {} --version {}'.format(
            resource_group, edge_action_name, version_name)).get_output_in_json()
        # Verify the response contains expected fields
        self.assertIsNotNone(result)
        self.assertTrue(result['name'])
        decoded = base64.b64decode(result['content'], validate=True)
        expected = base64.b64decode(test_content)
        # The service may package a file deployment as a ZIP on retrieval.
        if zipfile.is_zipfile(BytesIO(decoded)):
            with zipfile.ZipFile(BytesIO(decoded)) as archive:
                self.assertIn(expected, [archive.read(item) for item in archive.infolist() if not item.is_dir()])
        else:
            self.assertEqual(decoded, expected)

        # Clean up
        self.cmd('edge-action version delete -g {} --edge-action-name {} -n {} -y'.format(
            resource_group, edge_action_name, version_name))
        self.cmd('edge-action delete -g {} -n {} -y'.format(resource_group, edge_action_name))

    @ResourceGroupPreparer(additional_tags={'owner': 'edgeaction'})
    def test_edge_action_version_swap_default(self, resource_group):
        """Test Edge Action Version swap-default command.

        Creates two versions (v1 as default, v2 as non-default), deploys code to both,
        then swaps default to v2 and verifies the IsDefaultVersion property changed.
        This also tests the fix for the LRO poller NoneType error on swap-default.
        """
        edge_action_name = self.create_random_name(prefix='edgeaction', length=20)

        # Create edge action
        self.cmd('edge-action create -g {} -n {} --sku name=Standard tier=Standard --location global'.format(
            resource_group, edge_action_name))

        # Create v1 as default
        self.cmd('edge-action version create -g {} --edge-action-name {} -n v1 --deployment-type file --location global --is-default-version True'.format(
            resource_group, edge_action_name))

        # Deploy code to v1
        test_content = base64.b64encode(b'function handler(event) { return event; }').decode('utf-8')
        self.cmd('edge-action version deploy-version-code -g {} --edge-action-name {} --version v1 --name testcode --content "{}"'.format(
            resource_group, edge_action_name, test_content))

        # Create v2 as non-default
        self.cmd('edge-action version create -g {} --edge-action-name {} -n v2 --deployment-type file --location global --is-default-version False'.format(
            resource_group, edge_action_name))

        # Deploy code to v2
        self.cmd('edge-action version deploy-version-code -g {} --edge-action-name {} --version v2 --name testcode --content "{}"'.format(
            resource_group, edge_action_name, test_content))

        # Verify v1 is default before swap
        validation_checks = [JMESPathCheck('validationStatus != `null`', True)]
        self.cmd('edge-action version show -g {} --edge-action-name {} -n v1'.format(
            resource_group, edge_action_name),
            checks=validation_checks + [JMESPathCheck('isDefaultVersion', 'True')])
        self.cmd('edge-action version show -g {} --edge-action-name {} -n v2'.format(
            resource_group, edge_action_name),
            checks=validation_checks + [JMESPathCheck('isDefaultVersion', 'False')])

        # Swap default to v2
        self.cmd('edge-action version swap-default -g {} --edge-action-name {} --version v2'.format(
            resource_group, edge_action_name))

        # Verify v2 is now default after swap
        self.cmd('edge-action version show -g {} --edge-action-name {} -n v1'.format(
            resource_group, edge_action_name),
            checks=validation_checks + [JMESPathCheck('isDefaultVersion', 'False')])
        self.cmd('edge-action version show -g {} --edge-action-name {} -n v2'.format(
            resource_group, edge_action_name),
            checks=validation_checks + [JMESPathCheck('isDefaultVersion', 'True')])

        # Clean up
        self.cmd('edge-action version delete -g {} --edge-action-name {} -n v1 -y'.format(
            resource_group, edge_action_name))
        self.cmd('edge-action version delete -g {} --edge-action-name {} -n v2 -y'.format(
            resource_group, edge_action_name))
        self.cmd('edge-action delete -g {} -n {} -y'.format(resource_group, edge_action_name))

    @ResourceGroupPreparer(additional_tags={'owner': 'edgeaction'})
    def test_edge_action_execution_filter_crud(self, resource_group):
        """Test execution-filter CRUD and the customized update arguments."""
        edge_action_name = self.create_random_name(prefix='edgeaction', length=20)
        filter_name = self.create_random_name(prefix='filter', length=15)
        header_name = 'x-test-header'
        header_value = 'test-value'

        self.cmd('edge-action create -g {} -n {} --sku name=Standard tier=Standard --location global'.format(
            resource_group, edge_action_name))
        test_content = base64.b64encode(b'function handler(event) { return event; }').decode('utf-8')
        versions = {}
        for version_name, is_default in [('v1', 'True'), ('v2', 'False')]:
            versions[version_name] = self.cmd(
                'edge-action version create -g {} --edge-action-name {} -n {} '
                '--deployment-type file --location global --is-default-version {}'.format(
                    resource_group, edge_action_name, version_name, is_default)).get_output_in_json()
            self.cmd(
                'edge-action version deploy-version-code -g {} --edge-action-name {} '
                '--version {} --name testcode --content "{}"'.format(
                    resource_group, edge_action_name, version_name, test_content), checks=[
                        JMESPathCheck('provisioningState', 'Succeeded'),
                        JMESPathCheck('validationStatus', 'Succeeded'),
                ])

        # Test list execution filters (should be empty initially)
        list_checks = [JMESPathCheck('length(@)', 0)]
        self.cmd('edge-action execution-filter list -g {} --edge-action-name {}'.format(
            resource_group, edge_action_name), checks=list_checks)

        # Test create execution filter with all required parameters
        expected = {
            'name': filter_name,
            'versionId': versions['v1']['id'],
            'executionFilterIdentifierHeaderName': header_name,
            'executionFilterIdentifierHeaderValue': header_value,
            'provisioningState': 'Succeeded',
            'location': 'global',
        }
        create_checks = [JMESPathCheck(field, value) for field, value in expected.items()]
        self.cmd(
            'edge-action execution-filter create -g {} --edge-action-name {} -n {} '
            '--location global --version-id {} --execution-filter-identifier-header-name {} '
            '--execution-filter-identifier-header-value {}'.format(
                resource_group, edge_action_name, filter_name, versions['v1']['id'],
                header_name, header_value), checks=create_checks)

        show_command = 'edge-action execution-filter show -g {} --edge-action-name {} -n {}'.format(
            resource_group, edge_action_name, filter_name)
        update_command = 'edge-action execution-filter update -g {} --edge-action-name {} -n {}'.format(
            resource_group, edge_action_name, filter_name)
        self.cmd(show_command, checks=create_checks)
        updates = [
            ('--tags purpose=updated', {'tags': {'purpose': 'updated'}}),
            ('--execution-filter-identifier-header-name ' + header_name + '-updated',
             {'executionFilterIdentifierHeaderName': header_name + '-updated'}),
            ('--execution-filter-identifier-header-value ' + header_value + '-updated',
             {'executionFilterIdentifierHeaderValue': header_value + '-updated'}),
            ('--version-id ' + versions['v2']['id'], {'versionId': versions['v2']['id']}),
            ('--version-id {} --execution-filter-identifier-header-name {} '
             '--execution-filter-identifier-header-value {} --tags purpose=combined'.format(
                 versions['v1']['id'], header_name + '-combined', header_value + '-combined'), {
                     'versionId': versions['v1']['id'],
                     'executionFilterIdentifierHeaderName': header_name + '-combined',
                     'executionFilterIdentifierHeaderValue': header_value + '-combined',
                     'tags': {'purpose': 'combined'},
             }),
            ('--tags "{{}}"', {'tags': {}}),
            ('--execution-filter-identifier-header-value named-value '
             '--set execution_filter_identifier_header_value=true tags.number=123 --force-string', {
                 'executionFilterIdentifierHeaderValue': 'true',
                 'tags': {'number': '123'},
             }),
            ('--remove tags.number', {'tags': {}}),
        ]
        for options, changed_fields in updates:
            expected.update(changed_fields)
            update_checks = [JMESPathCheck(field, value) for field, value in expected.items()]
            self.cmd('{} {}'.format(update_command, options), checks=update_checks)
            self.cmd(show_command, checks=update_checks)

        # Test list execution filters (should contain 1 item now)
        list_checks = [JMESPathCheck('length(@)', 1)]
        self.cmd('edge-action execution-filter list -g {} --edge-action-name {}'.format(
            resource_group, edge_action_name), checks=list_checks)

        # Test delete execution filter
        self.cmd('edge-action execution-filter delete -g {} --edge-action-name {} -n {} -y'.format(
            resource_group, edge_action_name, filter_name))

        # Delete the non-default version before the default version.
        for version_name in ('v2', 'v1'):
            self.cmd('edge-action version delete -g {} --edge-action-name {} -n {} -y'.format(
                resource_group, edge_action_name, version_name))
        self.cmd('edge-action delete -g {} -n {} -y'.format(resource_group, edge_action_name))
