# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from knack.util import CLIError
from azure.cli.testsdk import (ScenarioTest, record_only)
from ..custom_preparers import (SpringPreparer, SpringResourceGroupPreparer)
from ..custom_dev_setting_constant import SpringTestEnvironmentEnum


class JobDeploy(ScenarioTest):

    @SpringResourceGroupPreparer(dev_setting_name=SpringTestEnvironmentEnum.ENTERPRISE['resource_group_name'])
    @SpringPreparer(**SpringTestEnvironmentEnum.ENTERPRISE['spring'])
    def test_asa_job_deploy(self, resource_group, spring):
        py_path = os.path.abspath(os.path.dirname(__file__))
        file_path = os.path.join(py_path, 'files/test1.jar').replace("\\", "/")
        self.kwargs.update({
            'job': 'myjob',
            'serviceName': spring,
            'rg': resource_group,
            'file': file_path
        })

        self.cmd('spring job create -n {job} -g {rg} -s {serviceName}', checks=[
            self.check('name', '{job}')
        ])

        # deploy unexist file, the fail is expected
        with self.assertRaisesRegex(CLIError, "artifact path {} does not exist.".format(file_path)):
            self.cmd('spring job deploy -n {job} -g {rg} -s {serviceName} --artifact-path {file}')
