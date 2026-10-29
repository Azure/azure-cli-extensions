# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.testsdk import ResourceGroupPreparer, JMESPathCheck
from azure.cli.testsdk import ScenarioTest, record_only
from .afdx_scenario_mixin import CdnAfdScenarioMixin
from azext_cdn.vendored_sdks.models import (AfdCertificateType, AfdMinimumTlsVersion)


class CdnAfdCustomDomainScenarioTest(CdnAfdScenarioMixin, ScenarioTest):
    @ResourceGroupPreparer(additional_tags={'owner': 'jingnanxu'})
    def test_afd_custom_domain_crud(self, resource_group):
        profile_name = self.create_random_name(prefix='profile', length=16)
        self.afd_custom_domain_list_cmd(resource_group, profile_name, expect_failure=True)

        # Create a standard Azure frontdoor profile
        self.afd_profile_create_cmd(resource_group, profile_name)
        with self.afd_byoc_identity(resource_group, profile_name):
            list_checks = [JMESPathCheck('length(@)', 0)]
            self.afd_custom_domain_list_cmd(resource_group, profile_name, checks=list_checks)

            # Create a secret
            secret_name = self.create_random_name(prefix='secret', length=24)
            secret_source = "/subscriptions/3c0124f9-e564-4c42-86f7-fa79457aedc3/resourceGroups/byoc/providers/Microsoft.KeyVault/vaults/Azure-CDN-BYOC/secrets/afde2e-root-azfdtest-xyz"
            use_latest_version = True
            secret_version = None

            checks = [JMESPathCheck('provisioningState', 'Succeeded')]
            secretData = self.afd_secret_create_cmd(resource_group,
                                                    profile_name,
                                                    secret_name,
                                                    secret_source,
                                                    use_latest_version,
                                                    secret_version,
                                                    checks=checks).get_output_in_json()
            secretId = secretData['id']

            custom_domain_name = self.create_random_name(prefix='customdomain', length=24)
            host_name = f"{custom_domain_name}.afde2e-root.azfdtest.xyz"
            certificate_type = AfdCertificateType.customer_certificate.value
            minimum_tls_version = AfdMinimumTlsVersion.tls12.value
            azure_dns_zone = None

            checks = [JMESPathCheck('domainValidationState', 'Approved')]
            self.afd_custom_domain_create_cmd(resource_group,
                                              profile_name,
                                              custom_domain_name,
                                              host_name,
                                              certificate_type,
                                              minimum_tls_version,
                                              azure_dns_zone,
                                              secretId,
                                              checks=checks)

            show_checks = [JMESPathCheck('name', custom_domain_name),
                           JMESPathCheck('domainValidationState', 'Approved'),
                           JMESPathCheck('hostName', host_name),
                           JMESPathCheck('tlsSettings.certificateType', certificate_type),
                           JMESPathCheck('tlsSettings.minimumTlsVersion', minimum_tls_version),
                           JMESPathCheck('tlsSettings.secret.id', secretId)]
            self.afd_custom_domain_show_cmd(resource_group, profile_name, custom_domain_name, checks=show_checks)

            list_checks = [JMESPathCheck('length(@)', 1),
                           JMESPathCheck('@[0].name', custom_domain_name),
                           JMESPathCheck('@[0].domainValidationState', 'Approved')]
            self.afd_custom_domain_list_cmd(resource_group, profile_name, checks=list_checks)

            self.cmd(f"afd custom-domain regenerate-validation-token -g {resource_group} "
                     f"--profile-name {profile_name} --custom-domain-name {custom_domain_name}")

            # Delete the custom domain
            self.afd_custom_domain_delete_cmd(resource_group, profile_name, custom_domain_name)
            list_checks = [JMESPathCheck('length(@)', 0)]
            self.afd_custom_domain_list_cmd(resource_group, profile_name, checks=list_checks)

    @ResourceGroupPreparer(additional_tags={'owner': 'zhefeng'})
    def test_afd_custom_domain_tls_groups_crud(self, resource_group):
        profile_name = self.create_random_name(prefix='profile', length=16)
        self.afd_profile_create_cmd(resource_group, profile_name)
        # RTMain requires the BYOC vault and profile to use the same subscription.
        vault_subscription = self.get_subscription_id()
        with self.afd_byoc_identity(
                resource_group, profile_name, vault_name='AfdxE2eTestKV04',
                vault_resource_group='DoNotDeleteThisRG', vault_subscription=vault_subscription):
            secret_name = self.create_random_name(prefix='secret', length=24)
            secret_source = (
                f'/subscriptions/{vault_subscription}/resourceGroups/DoNotDeleteThisRG'
                '/providers/Microsoft.KeyVault/vaults/AfdxE2eTestKV04/secrets/'
                'test-wildcard-domain-rollingrp-01-azfdtest-xyz-cert'
            )
            secret = self.afd_secret_create_cmd(
                resource_group, profile_name, secret_name, secret_source, True, None).get_output_in_json()
            custom_domain_name = self.create_random_name(prefix='customdomain', length=24)
            host_name = f'{custom_domain_name}.wildcard-domain.rprolling-01.azfdtest.xyz'
            profile_args = f'-g {resource_group} --profile-name {profile_name}'
            domain_args = f'{profile_args} --custom-domain-name {custom_domain_name}'

            create_checks = [
                JMESPathCheck('domainValidationState', 'Approved'),
                JMESPathCheck('tlsSettings.serverTlsGroupPolicy', 'Custom'),
                JMESPathCheck('length(tlsSettings.serverTlsGroups)', 2),
                JMESPathCheck("contains(tlsSettings.serverTlsGroups, 'X25519')", True),
                JMESPathCheck("contains(tlsSettings.serverTlsGroups, 'X25519MLKEM768')", True),
                JMESPathCheck('tlsSettings.secret.id', secret['id']),
            ]
            self.cmd(
                f'afd custom-domain create {domain_args} --host-name {host_name} '
                f'--certificate-type CustomerCertificate --minimum-tls-version TLS12 --secret {secret["id"]} '
                '--server-tls-group-policy Custom --server-tls-groups "[X25519,X25519MLKEM768]"',
                checks=create_checks)
            self.afd_custom_domain_show_cmd(
                resource_group, profile_name, custom_domain_name, checks=create_checks)

            update_checks = [
                JMESPathCheck('tlsSettings.serverTlsGroupPolicy', 'Custom'),
                JMESPathCheck('length(tlsSettings.serverTlsGroups)', 2),
                JMESPathCheck("contains(tlsSettings.serverTlsGroups, 'prime256v1')", True),
                JMESPathCheck("contains(tlsSettings.serverTlsGroups, 'SecP256r1MLKEM768')", True),
                JMESPathCheck('tlsSettings.secret.id', secret['id']),
            ]
            self.cmd(
                f'afd custom-domain update {domain_args} '
                '--server-tls-groups "[prime256v1,SecP256r1MLKEM768]"',
                checks=update_checks)
            self.afd_custom_domain_show_cmd(
                resource_group, profile_name, custom_domain_name, checks=update_checks)
            self.afd_custom_domain_list_cmd(resource_group, profile_name, checks=[
                JMESPathCheck('length(@)', 1),
                JMESPathCheck('[0].tlsSettings.serverTlsGroupPolicy', 'Custom'),
                JMESPathCheck('length([0].tlsSettings.serverTlsGroups)', 2),
                JMESPathCheck("contains([0].tlsSettings.serverTlsGroups, 'prime256v1')", True),
                JMESPathCheck("contains([0].tlsSettings.serverTlsGroups, 'SecP256r1MLKEM768')", True),
                JMESPathCheck('[0].tlsSettings.secret.id', secret['id']),
            ])
            self.afd_custom_domain_delete_cmd(resource_group, profile_name, custom_domain_name)
            self.afd_custom_domain_list_cmd(resource_group, profile_name, checks=[JMESPathCheck('length(@)', 0)])
