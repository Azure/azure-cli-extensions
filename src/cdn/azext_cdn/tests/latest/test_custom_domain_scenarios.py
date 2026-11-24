# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest

from azure.cli.testsdk import KeyVaultPreparer, JMESPathCheck
from azure.cli.testsdk import ScenarioTest
from .scenario_mixin import CdnScenarioMixin
from .config import fixture

from azure.core.exceptions import (HttpResponseError, ResourceNotFoundError, ResourceExistsError)
from knack.util import CLIError


# To run this test, please edit https://ms.portal.azure.com/#@microsoft.onmicrosoft.com/resource/subscriptions/27cafca8-b9a4-4264-b399-45d0c9cca1ab/resourceGroups/CliDevReservedGroup/providers/Microsoft.Network/dnszones/afdx-rp-platform-test.azfdtest.xyz/recordsets
class CdnCustomDomainScenarioTest(CdnScenarioMixin, ScenarioTest):
    subscription_fixture_by_test = {
        'test_cdn_custom_domain_byoc_latest': 'classic_byoc_latest_endpoint_id',
        'test_cdn_custom_domain_https_msft': 'classic_https_endpoint_id',
    }

    def test_cdn_custom_domain_errors(self):
        resource_group, profile_name = self.classic_cdn_profile()
        self.kwargs.update({
            'profile': profile_name,
            'endpoint': self.create_random_name(prefix='endpoint', length=24),
            'origin': 'www.test.com',
            'hostname': 'www.contoso.com',
            'name': 'customdomain1',
            'rg': resource_group,
        })

        self.endpoint_create_cmd(
            resource_group, self.kwargs['endpoint'], profile_name, self.kwargs['origin'])
        self.cmd('cdn custom-domain list -g {rg} --endpoint-name {endpoint} --profile-name {profile}')

        # These will all fail because we don't really have the ability to create the custom endpoint in test.
        # but they should still fail if there was a CLI-level regression.
        with self.assertRaises(HttpResponseError):
            self.cmd(
                'cdn custom-domain create -g {rg} --endpoint-name {endpoint} --hostname {hostname} --profile-name {profile} -n {name}')
        with self.assertRaises(ResourceNotFoundError):  # exits with code 3 due to missing resource
            self.cmd('cdn custom-domain show -g {rg} --endpoint-name {endpoint} --profile-name {profile} -n {name}')
        # self.cmd('cdn custom-domain delete -g {rg} --endpoint-name {endpoint} --profile-name {profile} -n {name} --yes')
        with self.assertRaises(ResourceNotFoundError):
            self.cmd(
                'cdn custom-domain enable-https -g {rg} --endpoint-name {endpoint} --profile-name {profile} -n {name}')

        with self.assertRaises(CLIError):
            self.cmd(
                'cdn custom-domain disable-https -g {rg} --endpoint-name {endpoint} --profile-name {profile} -n {name}')

    def test_cdn_custom_domain_crud(self):
        resource_group, profile_name = self.classic_cdn_profile()
        endpoint_name = 'aaz-06-01-crud'
        origin = 'www.microsoft1.com'
        self.endpoint_create_cmd(resource_group, endpoint_name, profile_name, origin)

        list_checks = [JMESPathCheck('length(@)', 0)]
        self.custom_domain_list_cmd(resource_group, profile_name, endpoint_name, checks=list_checks)

        custom_domain_name = self.create_random_name(prefix='customdomain', length=20)
        hostname = custom_domain_name + '.aaz0901.clitest.azfdtest.xyz'
        with self.assertRaises(HttpResponseError) as caught:
            self.custom_domain_create_cmd(group=resource_group,
                                          profile_name=profile_name,
                                          endpoint_name=endpoint_name,
                                          name=custom_domain_name,
                                          hostname=hostname)
        self.assertEqual(400, caught.exception.status_code)
        self.assertEqual('BadRequest', caught.exception.error.code)
        self.assertEqual(
            'Azure CDN from Microsoft (classic) no longer support new domain onboarding.',
            caught.exception.error.message)
        self.custom_domain_list_cmd(resource_group, profile_name, endpoint_name, checks=list_checks)
        with self.assertRaises(ResourceNotFoundError):
            self.custom_domain_show_cmd(resource_group, profile_name, endpoint_name, custom_domain_name)

    def test_cdn_custom_domain_https_msft(self):
        resource_group, profile_name, endpoint_name = self.classic_cdn_endpoint('classic_https_endpoint_id')
        custom_domain_name = "msft-0601-b"
        hostname = custom_domain_name + '-h.afdx-rp-platform-test.azfdtest.xyz'
        parameters = self._existing_https_parameters(
            resource_group, profile_name, endpoint_name, custom_domain_name, hostname, 'AzureKeyVault')
        self.assertEqual('b2f560488aef4b6d80ebd7d9e91578e9',
                         parameters['certificateSourceParameters']['secretVersion'])
        self._repeat_byoc_https(resource_group, profile_name, endpoint_name, custom_domain_name, parameters)

    def test_cdn_custom_domain_byoc_latest(self):
        resource_group, profile_name, endpoint_name = self.classic_cdn_endpoint('classic_byoc_latest_endpoint_id')
        custom_domain_name = "byoc"
        hostname = custom_domain_name + '-0601.afdx-rp-platform-test.azfdtest.xyz'
        parameters = self._existing_https_parameters(
            resource_group, profile_name, endpoint_name, custom_domain_name, hostname, 'AzureKeyVault')
        self.assertIsNone(parameters['certificateSourceParameters'].get('secretVersion'))
        self._repeat_byoc_https(resource_group, profile_name, endpoint_name, custom_domain_name, parameters)

    def _existing_https_parameters(self, group, profile, endpoint, domain, hostname, source):
        parameters = self.custom_domain_show_cmd(group, profile, endpoint, domain, checks=[
            JMESPathCheck('name', domain),
            JMESPathCheck('hostName', hostname),
            self._https_state_check(source),
            JMESPathCheck('customHttpsParameters.certificateSource', source),
            JMESPathCheck('customHttpsParameters.minimumTlsVersion', 'TLS12'),
        ]).get_output_in_json()['customHttpsParameters']
        self.assertEqual('ServerNameIndication', parameters['protocolType'])
        if source == 'AzureKeyVault':
            certificate = parameters['certificateSourceParameters']
            vault_id = fixture('byoc_vault_id')
            self.assertEqual(vault_id.split('/')[2], certificate['subscriptionId'])
            self.assertEqual(vault_id.split('/')[4].lower(), certificate['resourceGroupName'].lower())
            self.assertEqual(vault_id.split('/')[-1].lower(), certificate['vaultName'].lower())
            self.assertEqual(fixture('classic_byoc_secret_name'), certificate['secretName'])
        return parameters

    def _repeat_byoc_https(self, group, profile, endpoint, domain, parameters):
        certificate = parameters['certificateSourceParameters']
        self.custom_domain_enable_https_command(
            group, profile, endpoint, domain,
            user_cert_subscription_id=certificate['subscriptionId'],
            user_cert_group_name=certificate['resourceGroupName'],
            user_cert_vault_name=certificate['vaultName'],
            user_cert_secret_name=certificate['secretName'],
            user_cert_secret_version=certificate.get('secretVersion'),
            user_cert_protocol_type='sni',
            min_tls_version='1.2')
        self._assert_https_unchanged(group, profile, endpoint, domain, parameters)

    def _assert_https_unchanged(self, group, profile, endpoint, domain, parameters):
        self.custom_domain_show_cmd(group, profile, endpoint, domain, checks=[
            JMESPathCheck('customHttpsParameters', parameters),
            self._https_state_check(parameters['certificateSource']),
        ])

    @staticmethod
    def _https_state_check(source):
        pending = (
            'SubmittingDomainControlValidationRequest', 'PendingDomainControlValidationRequestApproval',
            'DomainControlValidationRequestApproved', 'IssuingCertificate', 'DeployingCertificate',
        ) if source == 'Cdn' else ('ImportingUserProvidedCertificate', 'DeployingCertificate')
        substate_check = ' || '.join("customHttpsProvisioningSubstate == '" + value + "'" for value in pending)
        return JMESPathCheck(
            "(customHttpsProvisioningState == 'Enabled' && customHttpsProvisioningSubstate == 'CertificateDeployed')"
            " || (customHttpsProvisioningState == 'Enabling' && (" + substate_check + "))",
            True)
