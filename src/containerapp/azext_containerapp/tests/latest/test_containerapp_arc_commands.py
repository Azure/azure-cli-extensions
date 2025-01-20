# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import ScenarioTest
from azure.cli.core.azclierror import ValidationError


class ContainerAppArcTest(ScenarioTest):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, random_config_dir=True, **kwargs)

    @AllowLargeResponse(8192)
    def test_containerapp_arc_invalid_command(self):
        with self.assertRaises(ValidationError) as cm:
            self.cmd('containerapp arc setup-core-dns --yes')
        self.assertIn("To setup core dns, Distro is required.", str(cm.exception))

        with self.assertRaises(ValidationError) as cm:
            self.cmd('containerapp arc setup-core-dns --distro Aks-Hci --yes')
        self.assertIn("'Aks-Hci' is not a valid value for '--distro' for core dns setup. ", str(cm.exception))
