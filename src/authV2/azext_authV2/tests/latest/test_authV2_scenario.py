# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.core.azclierror import ArgumentUsageError
from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class Authv2ScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_authV2')
    @AllowLargeResponse()
    def test_authV2_clientsecret_param_combinations(self, resource_group):
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
            JMESPathCheck('properties.platform.enabled', False)
        ])
        self.cmd('webapp auth config-version upgrade -g {} -n {}'.format(resource_group, webapp_name))

        # # update and verify
        self.cmd('webapp auth update -g {} -n {} --enabled true --runtime-version 1.2.8'
                .format(resource_group, webapp_name)).assert_with_checks([
                    JMESPathCheck('platform.enabled', True),
                    JMESPathCheck('platform.runtimeVersion', '1.2.8')
        ])
        
        with self.assertRaisesRegex(ArgumentUsageError, 'Usage Error: --client-secret and --client-secret-setting-name cannot both be '
                       'configured to non empty strings'):
            self.cmd('webapp auth Microsoft update -g {} -n {} --client-secret test --client-secret-setting-name test2'
                .format(resource_group, webapp_name))

        with self.assertRaisesRegex(ArgumentUsageError, 'Usage Error: --client-secret-setting-name and --thumbprint cannot both be '
                       'configured to non empty strings'):
            self.cmd('webapp auth Microsoft update -g {} -n {} --client-secret-setting-name test --thumbprint test2'
                .format(resource_group, webapp_name))

        with self.assertRaisesRegex(ArgumentUsageError, 'Usage Error: --client-secret and --thumbprint cannot both be '
                       'configured to non empty strings'):
            self.cmd('webapp auth Microsoft update -g {} -n {} --client-secret test --thumbprint test2'
                .format(resource_group, webapp_name))

        with self.assertRaisesRegex(ArgumentUsageError, 'Usage Error: --client-secret and --san cannot both be '
                       'configured to non empty strings'):
            self.cmd('webapp auth Microsoft update -g {} -n {} --client-secret test --san test2'
                .format(resource_group, webapp_name))

        with self.assertRaisesRegex(ArgumentUsageError, 'Usage Error: --client-secret-setting-name and --san cannot both be '
                       'configured to non empty strings'):
            self.cmd('webapp auth Microsoft update -g {} -n {} --client-secret-setting-name test --san test2'
                .format(resource_group, webapp_name))

        with self.assertRaisesRegex(ArgumentUsageError, 'Usage Error: --thumbprint and --san cannot both be '
                       'configured to non empty strings'):
            self.cmd('webapp auth Microsoft update -g {} -n {} --thumbprint test --san test2'
                .format(resource_group, webapp_name))

        with self.assertRaisesRegex(ArgumentUsageError, 'Usage Error: --san and --certificate-issuer must both be '
                       'configured to non empty strings'):
            self.cmd('webapp auth Microsoft update -g {} -n {} --san test'
                .format(resource_group, webapp_name))

        with self.assertRaisesRegex(ArgumentUsageError, 'Usage Error: --issuer and --tenant-id cannot be configured '
                       'to non empty strings at the same time.'):
            self.cmd('webapp auth Microsoft update -g {} -n {} --issuer test --tenant-id test2'
                .format(resource_group, webapp_name))

    @ResourceGroupPreparer(name_prefix='cli_test_authV2')
    @AllowLargeResponse()
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
            JMESPathCheck('properties.platform.enabled', False)
        ])
        
        self.cmd('webapp auth config-version upgrade -g {} -n {}'.format(resource_group, webapp_name))

        # # update and verify
        self.cmd('webapp auth update -g {} -n {} --enabled true --runtime-version 1.2.8'
                .format(resource_group, webapp_name)).assert_with_checks([
                    JMESPathCheck('platform.enabled', True),
                    JMESPathCheck('platform.runtimeVersion', '1.2.8')
        ])


    @ResourceGroupPreparer(name_prefix='cli_test_authV2')
    @AllowLargeResponse()
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

        # update
        result = self.cmd('webapp auth-classic update -g {} -n {} --enabled true --action LoginWithFacebook '
                 '--token-store false --token-refresh-extension-hours 7.2 --runtime-version 1.2.8 '
                 '--aad-client-id aad_client_id --aad-client-secret-certificate-thumbprint aad_thumbprint '
                 '--aad-allowed-token-audiences https://audience1 --aad-token-issuer-url https://issuer_url '
                 '--facebook-app-id facebook_id --facebook-oauth-scopes public_profile email'
                 .format(resource_group, webapp_name)).output
        self.assertEqual(result, "")

        # verify
        result = self.cmd('webapp auth-classic show -g {} -n {}'.format(resource_group, webapp_name)).assert_with_checks([
            JMESPathCheck('unauthenticatedClientAction', 'RedirectToLoginPage'),
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

    @ResourceGroupPreparer(name_prefix='cli_test_authV2')
    @AllowLargeResponse()
    def test_authV2_excluded_paths_parsing(self, resource_group):
        webapp_name = self.create_random_name('webapp-authentication-test', 40)
        plan_name = self.create_random_name('webapp-authentication-plan', 40)
        self.cmd(
            'appservice plan create -g {} -n {} --sku S1'.format(resource_group, plan_name))
        self.cmd(
            'webapp create -g {} -n {} --plan {}'.format(resource_group, webapp_name, plan_name))
        self.cmd('webapp auth config-version show -g {} -n {}'.format(resource_group, webapp_name)).assert_with_checks([
            JMESPathCheck('configVersion', 'v1')
        ])

        self.cmd('webapp auth show -g {} -n {}'.format(resource_group, webapp_name)).assert_with_checks([
            JMESPathCheck('properties.platform.enabled', False)
        ])
        self.cmd('webapp auth config-version upgrade -g {} -n {}'.format(resource_group, webapp_name))

        # # update and verify
        # test single path
        self.cmd('webapp auth update -g {} -n {} --enabled true --excluded-paths "/health"'
                .format(resource_group, webapp_name)).assert_with_checks([
                    JMESPathCheck('platform.enabled', True),
                    JMESPathCheck('globalValidation.excludedPaths[0]', '/health')
        ])

        # test multiple comma separated paths
        self.cmd('webapp auth update -g {} -n {} --excluded-paths "/health,/status,/metrics"'
                .format(resource_group, webapp_name)).assert_with_checks([
                    JMESPathCheck('globalValidation.excludedPaths[0]', '/health'),
                    JMESPathCheck('globalValidation.excludedPaths[1]', '/status'),
                    JMESPathCheck('globalValidation.excludedPaths[2]', '/metrics')
        ])

        # test JSON array format
        self.cmd('webapp auth update -g {} -n {} --excluded-paths \'["/api/health", "/api/status"]\''
                .format(resource_group, webapp_name)).assert_with_checks([
                    JMESPathCheck('globalValidation.excludedPaths[0]', '/api/health'),
                    JMESPathCheck('globalValidation.excludedPaths[1]', '/api/status')
        ])

        # test paths with special characters
        self.cmd('webapp auth update -g {} -n {} --excluded-paths "/api/v1/health,/webhook/callback"'
                .format(resource_group, webapp_name)).assert_with_checks([
                    JMESPathCheck('globalValidation.excludedPaths[0]', '/api/v1/health'),
                    JMESPathCheck('globalValidation.excludedPaths[1]', '/webhook/callback')
        ])

        # test single path without leading slash
        self.cmd('webapp auth update -g {} -n {} --excluded-paths "public"'
                .format(resource_group, webapp_name)).assert_with_checks([
                    JMESPathCheck('globalValidation.excludedPaths[0]', 'public')
        ])
