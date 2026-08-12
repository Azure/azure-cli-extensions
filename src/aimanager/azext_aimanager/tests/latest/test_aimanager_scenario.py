# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from azure.cli.testsdk.scenario_tests import AllowLargeResponse


class AIManagerScenarioTest(ScenarioTest):

    @AllowLargeResponse(size_kb=9999)
    @ResourceGroupPreparer(name_prefix='cli-aimgr-', random_name_length=16, location='eastus2')
    def test_aimanager(self):
        self.kwargs.update({
            'ai_manager_name': self.create_random_name(prefix='aim', length=12),
            'namespace_name': self.create_random_name(prefix='aimns', length=12),
            'location': 'eastus2',
        })

        # region AI Manager

        # create
        self.cmd(
            'aimanager create -g {rg} -n {ai_manager_name} -l {location} --delete-policy Keep',
            checks=[
                self.check('name', '{ai_manager_name}'),
                self.check('location', '{location}'),
                self.check('properties.deletePolicy', 'Keep'),
            ])

        # wait
        self.cmd('aimanager wait -g {rg} -n {ai_manager_name} --created', checks=[self.is_empty()])

        # show
        self.cmd('aimanager show -g {rg} -n {ai_manager_name}', checks=[
            self.check('name', '{ai_manager_name}'),
            self.check('properties.deletePolicy', 'Keep'),
        ])

        # list (resource group)
        self.cmd('aimanager list -g {rg}', checks=[
            self.check("length([?name=='{ai_manager_name}'])", 1),
        ])

        # update (tags + delete policy)
        self.cmd(
            'aimanager update -g {rg} -n {ai_manager_name} --tags env=test team=alpha --delete-policy Delete',
            checks=[
                self.check('name', '{ai_manager_name}'),
                self.check('tags.env', 'test'),
                self.check('tags.team', 'alpha'),
                self.check('properties.deletePolicy', 'Delete'),
            ])

        # endregion

        # region AI Manager namespace

        # add
        self.cmd(
            'aimanager namespace add -g {rg} -m {ai_manager_name} -n {namespace_name} '
            '--labels team=alpha --annotations owner=alice',
            checks=[
                self.check('name', '{namespace_name}'),
                self.check('properties.labels.team', 'alpha'),
                self.check('properties.annotations.owner', 'alice'),
            ])

        # wait
        self.cmd('aimanager namespace wait -g {rg} -m {ai_manager_name} -n {namespace_name} --created',
                 checks=[self.is_empty()])

        # show
        self.cmd('aimanager namespace show -g {rg} -m {ai_manager_name} -n {namespace_name}', checks=[
            self.check('name', '{namespace_name}'),
            self.check('properties.labels.team', 'alpha'),
        ])

        # list
        self.cmd('aimanager namespace list -g {rg} -m {ai_manager_name}', checks=[
            self.check("length([?name=='{namespace_name}'])", 1),
        ])

        # update (labels)
        self.cmd(
            'aimanager namespace update -g {rg} -m {ai_manager_name} -n {namespace_name} '
            '--labels team=beta --annotations owner=bob',
            checks=[
                self.check('name', '{namespace_name}'),
                self.check('properties.labels.team', 'beta'),
                self.check('properties.annotations.owner', 'bob'),
            ])

        # namespace get-credentials (print to stdout to avoid touching local kubeconfig)
        self.cmd('aimanager namespace get-credentials -g {rg} -m {ai_manager_name} -n {namespace_name} -f -')

        # delete namespace
        self.cmd('aimanager namespace delete -g {rg} -m {ai_manager_name} -n {namespace_name} --yes')

        # endregion

        # get-credentials (print to stdout to avoid touching local kubeconfig)
        self.cmd('aimanager get-credentials -g {rg} -n {ai_manager_name} -f -')

        # delete AI Manager
        self.cmd('aimanager delete -g {rg} -n {ai_manager_name} --yes')
