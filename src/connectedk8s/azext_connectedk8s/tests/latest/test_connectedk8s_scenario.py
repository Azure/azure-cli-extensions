# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)  # pylint: disable=import-error
from azure_devtools.scenario_tests import AllowLargeResponse  # pylint: disable=import-error


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


def _get_test_data_file(filename):
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(curr_dir, 'data', filename).replace('\\', '\\\\')


class Connectedk8sScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_connectedk8s')
    def test_connectedk8s(self, resource_group):

        self.kwargs.update({
            'name': 'test1',
            'kubeconfig': "%s" % (_get_test_data_file('config.yaml'))
        })
        os.environ['HELMCHART'] = _get_test_data_file('setupChart-0.1.19.tgz')
        self.cmd('connectedk8s connect -g {rg} -n {name} -l eastus2euap --tags foo=doo --kube-config {kubeconfig}', checks=[
            self.check('tags.foo', 'doo'),
            self.check('name', '{name}')
        ])
        self.cmd('connectedk8s show -g {rg} -n {name}', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', '{rg}'),
            self.check('tags.foo', 'doo')
        ])
        self.cmd('connectedk8s delete -g {rg} -n {name} --kube-config {kubeconfig} -y')
