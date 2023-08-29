# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long,unused-argument

import json
import unittest
from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
import os
import urllib
import time


def _get_test_data_file(filename):
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(curr_dir, 'data', filename).replace('\\', '\\\\')


class AzureMeshServiceScenarioTest(ScenarioTest):

    @unittest.skip('sfmergeutility.sf_merge_utility bug')
    @ResourceGroupPreparer(name_prefix='cli_test_mesh_')
    def test_merge_utility(self, resource_group):
        app_name = 'helloWorldApp'
        yaml_files_path = "%s,%s,%s" % (_get_test_data_file('app.yaml'), _get_test_data_file('service.yaml'), _get_test_data_file('network.yaml'))
        self.kwargs.update({
            'resource_id': '',
            'resource_group': resource_group,
            'deployment_name': self.create_random_name(prefix='cli', length=24),
            'app_name': app_name,
            'input_yaml_files': yaml_files_path
        })

        # Test create
        self.cmd('az mesh deployment create -g {rg} --input-yaml-files {input_yaml_files} --name {deployment_name}')

        # Test delete
        self.cmd('az mesh app delete -g {rg} --name {app_name} --yes')

        # Delete the generated ARM template
        os.path.delete(os.path.combine(os.curdir(), 'merged-arm_rp.json'))

    @ResourceGroupPreparer(random_name_length=20)
    def test_app_commands(self, resource_group):
        app_name = 'helloWorldApp'
        self.kwargs.update({
            'resource_id': '',
            'resource_group': resource_group,
            'deployment_name': self.create_random_name(prefix='cli', length=24),
            'app_name': app_name,
            'template_location': _get_test_data_file('template1.json')
        })

        # Test create
        self.cmd('az mesh deployment create -g {rg} --template-file {template_location} --name {deployment_name} --no-wait')
        time.sleep(10)

        # Test list
        app_list = self.cmd('az mesh app list --resource-group {rg}', checks=[
            self.check('[0].name', app_name)
        ]).get_output_in_json()
        assert len(app_list) == 1

        # Test show resource group/name
        data = self.cmd('az mesh app show --resource-group {rg} --name {app_name}', checks=[
            self.exists('description'),
            self.check('healthState', 'Ok'),
            self.exists('id'),
            self.exists('location'),
            self.check('name', app_name),
            # self.check('provisioningState', 'Succeeded'),  # ClusterAllocationInsufficientCapacity
            self.exists('serviceNames'),
            self.check('resourceGroup', resource_group.upper()),
            # self.check('status', 'Ready'),  # ClusterAllocationInsufficientCapacity
            self.exists('type')
        ]).get_output_in_json()
        resource_id = data['id']

        # Test show resource id
        show_data = self.cmd('az mesh app show --id {0}'.format(resource_id)).get_output_in_json()

        assert data == show_data

        # Test delete
        self.cmd('az mesh app delete -g {rg} --name {app_name} --yes')

        app_list = self.cmd('az mesh app list --resource-group {rg}').get_output_in_json()
        assert len(app_list) == 0

    @ResourceGroupPreparer(random_name_length=20)
    def test_service_commands(self, resource_group):
        app_name = 'helloWorldApp'

        self.kwargs.update({
            'resource_id': '',
            'resource_group': resource_group,
            'deployment_name': self.create_random_name(prefix='cli', length=24),
            'app_name': app_name,
            'service_name': 'helloWorldService',
            'template_location': _get_test_data_file('template1.json')

        })

        self.cmd('az mesh deployment create -g {rg} --template-file {template_location} --name {deployment_name} --no-wait')
        time.sleep(10)

        app_list = self.cmd('az mesh app list --resource-group {rg}', checks=[
            self.check('[0].name', app_name)
        ]).get_output_in_json()
        assert len(app_list) == 1

        # Test list
        service_list = self.cmd('az mesh service list --resource-group {rg} --app-name {app_name}', checks=[

        ]).get_output_in_json()
        assert len(service_list) == 1

        # Test show
        self.cmd('az mesh service show --resource-group {rg} --app-name {app_name} --name {service_name}', checks=[])

        self.cmd('az mesh app delete -g {rg} --name {app_name} --yes')

    @unittest.skip('ClusterAllocationInsufficientCapacity')
    @ResourceGroupPreparer(random_name_length=20)
    def test_service_replica_commands(self, resource_group):
        app_name = 'helloWorldApp'

        self.kwargs.update({
            'resource_group': resource_group,
            'deployment_name': self.create_random_name(prefix='cli', length=24),
            'app_name': app_name,
            'service_name': 'helloWorldService',
            'replica_name': 0,
            'template_location': _get_test_data_file('template1.json')
        })

        self.cmd('az mesh deployment create -g {rg} --template-file {template_location} --name {deployment_name}')

        app_list = self.cmd('az mesh app list --resource-group {rg}', checks=[
            self.check('[0].name', app_name)
        ]).get_output_in_json()
        assert len(app_list) == 1

        # Test list
        service_list = self.cmd('az mesh service-replica list --resource-group {rg} --app-name {app_name} --service-name {service_name}',).get_output_in_json()
        assert len(service_list) == 1

        # Test show
        self.cmd('az mesh service-replica show --resource-group {rg} --app-name {app_name} --service-name {service_name} --replica-name {replica_name}', checks=[
            self.exists('codePackages'),
            self.exists('networkRefs'),
            self.exists('osType'),
            self.exists('replicaName'),
        ])

        self.cmd('az mesh app delete -g {rg} --name {app_name} --yes')

    @unittest.skip('ClusterAllocationInsufficientCapacity')
    @ResourceGroupPreparer(random_name_length=20)
    def test_code_package_log_commands(self, resource_group):
        app_name = 'helloWorldApp'

        self.kwargs.update({
            'resource_group': resource_group,
            'deployment_name': self.create_random_name(prefix='cli', length=24),
            'app_name': app_name,
            'service_name': 'helloWorldService',
            'replica_name': 0,
            'template_location': _get_test_data_file('template1.json'),
            'code_package_name': 'helloWorldCode',
            'network_name': 'helloWorldNetwork'
        })

        self.cmd('az mesh deployment create -g {rg} --template-file {template_location} --name {deployment_name}')

        network_info = self.cmd('az mesh network show -g {rg} -n {network_name}').get_output_in_json()
        ip = network_info["ingressConfig"]["publicIpAddress"]
        urllib.urlopen('http://' + ip)

        # Test log
        self.cmd('az mesh code-package-log get --app-name {app_name} --code-package-name helloWorldCode  --replica-name {replica_name} --resource-group {rg} --service-name {service_name} ', checks=[
            self.exists('content')
        ])

        self.cmd('az mesh app delete -g {rg} --name {app_name} --yes')


if __name__ == '__main__':
    unittest.main()
