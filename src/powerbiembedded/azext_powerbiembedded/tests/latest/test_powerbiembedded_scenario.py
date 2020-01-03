# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class PowerBIEmbeddedScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_powerbi_embedded', location='southcentralus')
    def test_powerbi_embedded(self, resource_group):
        self.kwargs.update({
            'wc': 'mycli-powerbi-wc',
            'rg': resource_group
        })
        self.cmd('powerbi-embedded workspace-collection create -g {rg} -n {wc} --tags owner=cli', checks=[
            self.check('type', 'Microsoft.PowerBI/workspaceCollections'),
            self.check('tags.owner', 'cli')
        ])
        self.cmd('powerbi-embedded workspace-collection update -g {rg} -n {wc} --tags owner=mycli', checks=[
            self.check('tags.owner', 'mycli')
        ])
        self.cmd('powerbi-embedded workspace-collection show -g {rg} -n {wc}', checks=[
            self.check('type', 'Microsoft.PowerBI/workspaceCollections')
        ])
        self.cmd('powerbi-embedded workspace-collection list -g {rg}', checks=[
            self.check('length(@)', 1)
        ])
        self.cmd('powerbi-embedded workspace-collection get-access-keys -g {rg} -n {wc}', checks=[
            self.check("contains(keys(@), 'key1')", True),
            self.check("contains(keys(@), 'key2')", True)
        ])
        self.cmd('powerbi-embedded workspace-collection regenerate-key -g {rg} -n {wc}', checks=[
            self.check("contains(keys(@), 'key1')", True),
            self.check("contains(keys(@), 'key2')", True)
        ])
        self.cmd('powerbi-embedded workspace-collection workspace list -g {rg} --workspace-collection-name {wc}')
        self.cmd('powerbi-embedded workspace-collection delete -g {rg} -n {wc}')
