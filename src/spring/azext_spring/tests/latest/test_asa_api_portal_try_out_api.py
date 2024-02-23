# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from azure.cli.testsdk import (ScenarioTest, record_only)

# pylint: disable=line-too-long
# pylint: disable=too-many-lines


"""
Mark record_only to use the recording files as the mocked server to run the tests.
"""


@record_only()
class ApiPortalTryOutApiTest(ScenarioTest):

    def test_try_out_api_for_api_portal(self):
        self.kwargs.update({
            'serviceName': 'df-ae-enterpri-1108020957',
            'rg': 'ASCIT-Enterprise-20231108',
        })

        self.cmd('spring api-portal update -g {rg} -s {serviceName} --enable-api-try-out',
                 self.check('properties.apiTryOutEnabledState', 'Enabled'))

        # When don't change anything
        self.cmd('spring api-portal update -g {rg} -s {serviceName}',
                 self.check('properties.apiTryOutEnabledState', 'Enabled'))

        self.cmd('spring api-portal update -g {rg} -s {serviceName} --enable-api-try-out false',
                 self.check('properties.apiTryOutEnabledState', 'Disabled'))

        self.cmd('spring api-portal update -g {rg} -s {serviceName} --enable-api-try-out true',
                 self.check('properties.apiTryOutEnabledState', 'Enabled'))
