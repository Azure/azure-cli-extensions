# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

import os
from azure.cli.testsdk import (ScenarioTest, record_only)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class K8sExtensionScenarioTest(ScenarioTest):
    @record_only()
    def test_k8s_extension(self):
        resource_type = 'microsoft.openservicemesh'
        self.kwargs.update({
            'name': 'openservicemesh',
            'rg': 'nanthirg0923',
            'cluster_name': 'nanthicluster0923',
            'cluster_type': 'connectedClusters',
            'extension_type': resource_type,
            'release_train': 'pilot',
            'version': '0.8.3'
        })

        self.cmd('k8s-extension create -g {rg} -n {name} -c {cluster_name} --cluster-type {cluster_type} '
                 '--extension-type {extension_type} --release-train {release_train} --version {version}',
                 checks=[
                     self.check('name', '{name}'),
                     self.check('releaseTrain', '{release_train}'),
                     self.check('version', '{version}'),
                     self.check('resourceGroup', '{rg}'),
                     self.check('extensionType', '{extension_type}')
                 ]
                )

        # Update is disabled for now
        # self.cmd('k8s-extension update -g {rg} -n {name} --tags foo=boo', checks=[
        #     self.check('tags.foo', 'boo')
        # ])

        installed_exts = self.cmd('k8s-extension list -c {cluster_name} -g {rg} --cluster-type {cluster_type}').get_output_in_json()
        found_extension = False
        for item in installed_exts:
            if item['extensionType'] == resource_type:
                found_extension = True
                break
        self.assertTrue(found_extension)

        self.cmd('k8s-extension show -c {cluster_name} -g {rg} -n {name} --cluster-type {cluster_type}', checks=[
            self.check('name', '{name}'),
            self.check('releaseTrain', '{release_train}'),
            self.check('version', '{version}'),
            self.check('resourceGroup', '{rg}'),
            self.check('extensionType', '{extension_type}')
        ])

        self.cmd('k8s-extension delete -g {rg} -c {cluster_name} -n {name} --cluster-type {cluster_type} -y')

        installed_exts = self.cmd('k8s-extension list -c {cluster_name} -g {rg} --cluster-type {cluster_type}').get_output_in_json()
        found_extension = False
        for item in installed_exts:
            if item['extensionType'] == resource_type:
                found_extension = True
                break
        self.assertFalse(found_extension)
