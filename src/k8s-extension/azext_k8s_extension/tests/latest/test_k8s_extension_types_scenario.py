# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

import os
from azure.cli.testsdk import (ScenarioTest, record_only)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class K8sExtensionTypesScenarioTest(ScenarioTest):
    @record_only()
    def test_k8s_extension_types(self):
        extension_type = 'microsoft.contoso.samples'
        self.kwargs.update({
            'rg': 'azurecli-tests',
            'cluster_name': 'arc-cluster',
            'cluster_type': 'connectedClusters',
            'extension_type': extension_type,
            'location': 'eastus2euap',
            'version': '1.1.0'
        })

        self.cmd('k8s-extension extension-types show-by-cluster -g {rg} -c {cluster_name} --cluster-type {cluster_type} '
                 '--extension-type {extension_type}', checks=[
                     self.check('name', '{extension_type}')
                 ])
        
        self.cmd('k8s-extension extension-types show-by-location -l {location} '
                 '--extension-type {extension_type}', checks=[
                     self.check('name', '{extension_type}')
                 ])
        
        extensionTypes_list = self.cmd('k8s-extension extension-types list-by-cluster -g {rg} -c {cluster_name} '
                                       '--cluster-type {cluster_type}').get_output_in_json()
        assert len(extensionTypes_list) > 0

        extensionTypes_locationList = self.cmd('k8s-extension extension-types list-by-location --location {location}').get_output_in_json()
        assert len(extensionTypes_locationList) > 0

        extensionTypes_list = self.cmd('k8s-extension extension-types list-versions-by-cluster -g {rg} -c {cluster_name} --cluster-type {cluster_type} --extension-type {extension_type}').get_output_in_json()

        assert len(extensionTypes_list) > 0

        extensionTypes_list = self.cmd('k8s-extension extension-types list-versions-by-location --location {location} --extension-type {extension_type}').get_output_in_json()

        assert len(extensionTypes_list) > 0

        extensionTypes_list = self.cmd('k8s-extension extension-types show-version-by-cluster -g {rg} -c {cluster_name} --cluster-type {cluster_type} --extension-type {extension_type} --version {version}').get_output_in_json()

        assert len(extensionTypes_list) > 0

        extensionTypes_list = self.cmd('k8s-extension extension-types show-version-by-location --location {location} --extension-type {extension_type} --version {version}').get_output_in_json()

        assert len(extensionTypes_list) > 0



