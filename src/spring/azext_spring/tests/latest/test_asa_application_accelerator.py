# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk import (ScenarioTest, record_only)

# pylint: disable=line-too-long
# pylint: disable=too-many-lines


@record_only()
class ApiApplicationAcceleratorTest(ScenarioTest):

    def test_application_accelerator(self):
        
        self.kwargs.update({
            'serviceName': 'acc-test',
            'rg': 'acc'
        })

        self.cmd('spring application-accelerator create -g {rg} -s {serviceName}', 
        checks=[
            self.check('properties.provisioningState', "Succeeded")
        ])

        self.cmd('spring application-accelerator show -g {rg} -s {serviceName}', 
        checks=[
            self.check('properties.provisioningState', "Succeeded")
        ])

        self.cmd('spring application-accelerator delete -g {rg} -s {serviceName}')
