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
        extension_type = 'cassandradatacentersoperator'
        self.kwargs.update({
            'rg': 'clitest-rg', #K8sPartnerExtensionTest',
            'cluster_name': 'kind-clitest-cluster',#'k8s-extension-cluster-32469-arc',
            'cluster_type': 'connectedClusters',
            'extension_type': extension_type,
            'location': 'eastus2euap'
        })

        self.cmd('k8s-extension extension-types show -g {rg} -c {cluster_name} --cluster-type {cluster_type} '
                 '--extension-type {extension_type}', checks=[
                     self.check('name', '{extension_type}')
                 ])
        
        extensionTypes_list = self.cmd('k8s-extension extension-types list -g {rg} -c {cluster_name} '
                                       '--cluster-type {cluster_type}').get_output_in_json()
        assert len(extensionTypes_list) > 0

        extensionTypes_locationList = self.cmd('k8s-extension extension-types list-by-location --location '
                                               '{location}').get_output_in_json()
        assert len(extensionTypes_locationList) > 0

        self.cmd('k8s-extension extension-types list-versions --location {location} --extension-type {extension_type}')
