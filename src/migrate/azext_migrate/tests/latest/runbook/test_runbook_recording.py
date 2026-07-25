# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk import ScenarioTest

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

# Runbooks require a pre-existing migrate project, wave, and generated
# runbook, none of which a ResourceGroupPreparer can provision. The scenario
# therefore targets a fixed, pre-provisioned runbook; the recording scrubs the
# subscription id, so playback needs no live resources.
PROJECT_RG = "BP_AE_Can"
PROJECT_NAME = "BP-AE-Can-Proj"
RUNBOOK_NAME = "testrunbook1"


class RunbookScenario(ScenarioTest):
    """Recorded read scenario for the runbook show/list commands."""

    def test_runbook_show_and_list(self):
        self.kwargs.update({
            'rg': PROJECT_RG,
            'project': PROJECT_NAME,
            'name': RUNBOOK_NAME,
        })

        self.cmd(
            'migrate runbook show -g {rg} --project-name {project} '
            '-n {name}',
            checks=[
                self.check('name', '{name}'),
                self.check('type', 'Microsoft.Migrate/MigrateProjects/'
                           'Runbooks'),
            ])

        self.cmd(
            'migrate runbook list -g {rg} --project-name {project}',
            checks=[self.check("length([?name=='{name}'])", 1)])


if __name__ == '__main__':
    unittest.main()
