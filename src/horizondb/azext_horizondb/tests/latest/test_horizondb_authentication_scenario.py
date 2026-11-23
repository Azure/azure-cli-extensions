# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import secrets
from contextlib import ExitStack
from unittest.mock import patch

from azure.cli.testsdk import ResourceGroupPreparer, ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

from .constants import CLUSTER_NAME_MAX_LENGTH, CLUSTER_NAME_PREFIX, JAPANEAST
from .recording_processors import ArmOperationResultsRecordingProcessor


class AuthenticationResourceGroupPreparer(ResourceGroupPreparer):
    def create_resource(self, name, **kwargs):
        args = super().create_resource(name, **kwargs)
        if self.dev_setting_name and self.test_class_instance.in_recording:
            self.test_class_instance.name_replacer.register_name_pair(self.dev_setting_name, self.moniker)
        return args


class HorizonDBAuthenticationScenarioTest(ScenarioTest):

    def __init__(self, method_name):
        processor = ArmOperationResultsRecordingProcessor()
        super().__init__(method_name, recording_processors=[processor], replay_processors=[processor])

    def setUp(self):
        # Without a cassette the test SDK otherwise records even in playback mode.
        if self.in_recording and not self.is_live:
            self.skipTest('Authentication cassette missing; record explicitly in a disposable subscription.')
        super().setUp()

    @AllowLargeResponse()
    @AuthenticationResourceGroupPreparer(name_prefix='cli_test_horizondb_auth_', location=JAPANEAST)
    def test_horizondb_authentication(self, resource_group):
        self.kwargs.update(rg=resource_group, location=JAPANEAST,
                           cluster=self.create_random_name(CLUSTER_NAME_PREFIX, CLUSTER_NAME_MAX_LENGTH))
        self.cmd('horizondb cluster create -g {rg} -n {cluster} --location {location} '
                 '--version 17 --geo-redundancy Disabled --public-access Disabled')
        with ExitStack() as cleanup:
            cleanup.callback(self.cmd, 'horizondb cluster delete -g {rg} -n {cluster} --yes')
            self.cmd('horizondb cluster pool create -g {rg} --cluster-name {cluster} -n authpool '
                     '--compute-generation 1 --compute-processor Intel --v-cores 2 '
                     '--node-count 1 --high-availability-mode Disabled')
            cleanup.callback(self.cmd, 'horizondb cluster pool delete -g {rg} --cluster-name {cluster} -n authpool --yes')
            self._check_authentication()

    def _check_authentication(self):
        scope = ' -g {rg} --cluster-name {cluster}'
        auth = 'horizondb cluster authentication '
        password = auth + 'password '
        self.cmd(auth + 'list' + scope, checks=[
            self.check("[?name=='passwordMethod'] | length(@)", 1),
            self.check("[?name=='microsoftEntra'] | length(@)", 1),
        ])

        # Keep the live credential out of command lines and replace it in the VCR traffic.
        placeholder = 'REDACTED-password-1!'
        secret = 'Aa1!' + secrets.token_hex(24) if self.in_recording else placeholder
        self.name_replacer.register_name_pair(secret, placeholder)
        with patch('azure.cli.core.aaz._prompt.prompt_pass', return_value=secret):
            self.cmd(password + 'create' + scope + ' --state Enabled --administrator-login scenarioadmin '
                     '--admin-password')
        self.cmd(password + 'wait' + scope + " --custom \"properties.state == 'Enabled'\" --timeout 120")
        self.cmd(password + 'show' + scope, checks=[
            self.check('properties.state', 'Enabled'),
            self.check('properties.administratorLogin', 'scenarioadmin'),
            self.check('contains(keys(properties), `\"administratorLoginPassword\"`)', False),
        ])
        # Reset the password without disabling the cluster's only authentication method.
        rotated = 'Bb2!' + secrets.token_hex(24) if self.in_recording else placeholder
        self.name_replacer.register_name_pair(rotated, placeholder)
        with patch('azure.cli.core.aaz._prompt.prompt_pass', return_value=rotated):
            self.cmd(password + 'update' + scope + ' --admin-password', checks=[
                self.check('properties.state', 'Enabled'),
                self.check('properties.administratorLogin', 'scenarioadmin'),
            ])
