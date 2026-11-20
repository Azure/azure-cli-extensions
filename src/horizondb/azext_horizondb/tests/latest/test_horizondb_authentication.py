# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import secrets
from unittest.mock import patch

from azure.cli.testsdk import ResourceGroupPreparer, ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

from .constants import CLUSTER_NAME_MAX_LENGTH, CLUSTER_NAME_PREFIX, JAPANEAST


class HorizonDBAuthenticationScenarioTest(ScenarioTest):

    def setUp(self):
        # Without a cassette the test SDK otherwise records even in playback mode.
        if self.in_recording and not self.is_live:
            self.skipTest('Authentication cassette missing; record explicitly in a disposable subscription.')
        super().setUp()

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_horizondb_auth_', location=JAPANEAST)
    def test_horizondb_authentication(self, resource_group):
        self.kwargs.update(rg=resource_group, location=JAPANEAST,
                           cluster=self.create_random_name(CLUSTER_NAME_PREFIX, CLUSTER_NAME_MAX_LENGTH))
        self.cmd('horizondb cluster create -g {rg} -n {cluster} --location {location} '
                 '--version 17 --geo-redundancy Disabled --public-access Disabled')
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
                     '--admin-password --no-wait')
        self.cmd(password + 'wait' + scope + ' --created')
        self.cmd(password + 'show' + scope, checks=[
            self.check('properties.state', 'Enabled'),
            self.check('properties.administratorLogin', 'scenarioadmin'),
            self.check('contains(keys(properties), `\"administratorLoginPassword\"`)', False),
        ])
        self.cmd(password + 'update' + scope + ' --state Disabled', checks=self.check('properties.state', 'Disabled'))
