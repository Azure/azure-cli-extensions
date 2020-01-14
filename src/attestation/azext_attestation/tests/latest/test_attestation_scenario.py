# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class AttestationScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_attestation')
    def test_attestation(self, resource_group):

        self.cmd('az attestation operation list',
                 checks=[])

        self.cmd('az attestation attestation-provider create '
                 '--resource-group {rg} '
                 '--name "MyAttestationProvider"',
                 checks=[])

        self.cmd('az attestation attestation-provider show '
                 '--resource-group {rg} '
                 '--name "MyAttestationProvider"',
                 checks=[])

        self.cmd('az attestation attestation-provider list',
                 checks=[])

        self.cmd('az attestation attestation-provider list '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az attestation attestation-provider delete '
                 '--resource-group {rg} '
                 '--name "MyAttestationProvider"',
                 checks=[])
