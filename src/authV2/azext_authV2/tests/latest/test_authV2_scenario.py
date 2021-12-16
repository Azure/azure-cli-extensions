# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class Authv2ScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_authV2')
    def test_authV2_auth(self, resource_group):
        webapp_name = self.create_random_name('webapp-authentication-test', 40)
        plan_name = self.create_random_name('webapp-authentication-plan', 40)
        self.cmd(
            'appservice plan create -g {} -n {} --sku S1'.format(resource_group, plan_name))
        self.cmd(
            'webapp create -g {} -n {} --plan {}'.format(resource_group, webapp_name, plan_name))
        self.cmd('webapp auth config-version show -g {} -n {}'.format(resource_group, webapp_name)).assert_with_checks([
            JMESPathCheck('configVersion', 'v1')
        ])

        # testing show command for newly created app and initial fields
        self.cmd('webapp auth show -g {} -n {}'.format(resource_group, webapp_name)).assert_with_checks([
            JMESPathCheck('properties', {})
        ])

        # # update and verify
        self.cmd('webapp auth update -g {} -n {} --enabled true --runtime-version 1.2.8'
                .format(resource_group, webapp_name)).assert_with_checks([
                    JMESPathCheck('platform', "{'enabled': True, 'runtimeVersion': '1.2.8'}")
        ])


    @ResourceGroupPreparer(name_prefix='cli_test_authV2')
    def test_authV2_authclassic(self, resource_group):
        webapp_name = self.create_random_name('webapp-authentication-test', 40)
        plan_name = self.create_random_name('webapp-authentication-plan', 40)
        self.cmd(
            'appservice plan create -g {} -n {} --sku S1'.format(resource_group, plan_name))
        self.cmd(
            'webapp create -g {} -n {} --plan {}'.format(resource_group, webapp_name, plan_name))
        self.cmd('webapp auth config-version show -g {} -n {}'.format(resource_group, webapp_name)).assert_with_checks([
            JMESPathCheck('configVersion', 'v1')
        ])

        # testing show command for newly created app and initial fields
        self.cmd('webapp auth-classic show -g {} -n {}'.format(resource_group, webapp_name)).assert_with_checks([
            JMESPathCheck('unauthenticatedClientAction', None),
            JMESPathCheck('defaultProvider', None),
            JMESPathCheck('enabled', False),
            JMESPathCheck('tokenStoreEnabled', None),
            JMESPathCheck('allowedExternalRedirectUrls', None),
            JMESPathCheck('tokenRefreshExtensionHours', None),
            JMESPathCheck('runtimeVersion', None),
            JMESPathCheck('clientId', None),
            JMESPathCheck('clientSecretCertificateThumbprint', None),
            JMESPathCheck('allowedAudiences', None),
            JMESPathCheck('issuer', None),
            JMESPathCheck('facebookAppId', None),
            JMESPathCheck('facebookOauthScopes', None)
        ])

        # update and verify
        result = self.cmd('webapp auth-classic update -g {} -n {} --enabled true --action LoginWithFacebook '
                          '--token-store false --token-refresh-extension-hours 7.2 --runtime-version 1.2.8 '
                          '--aad-client-id aad_client_id --aad-client-secret-certificate-thumbprint aad_thumbprint '
                          '--aad-allowed-token-audiences https://audience1 --aad-token-issuer-url https://issuer_url '
                          '--facebook-app-id facebook_id --facebook-oauth-scopes public_profile email'
                          .format(resource_group, webapp_name)).assert_with_checks([
                              JMESPathCheck(
                                  'unauthenticatedClientAction', 'RedirectToLoginPage'),
                              JMESPathCheck('defaultProvider', 'Facebook'),
                              JMESPathCheck('enabled', True),
                              JMESPathCheck('tokenStoreEnabled', False),
                              JMESPathCheck('tokenRefreshExtensionHours', 7.2),
                              JMESPathCheck('runtimeVersion', '1.2.8'),
                              JMESPathCheck('clientId', 'aad_client_id'),
                              JMESPathCheck('clientSecretCertificateThumbprint', 'aad_thumbprint'),
                              JMESPathCheck('issuer', 'https://issuer_url'),
                              JMESPathCheck('facebookAppId', 'facebook_id')]).get_output_in_json()

        self.assertIn('https://audience1', result['allowedAudiences'])