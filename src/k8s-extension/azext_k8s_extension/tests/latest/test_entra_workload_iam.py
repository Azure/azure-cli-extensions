# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=protected-access

import unittest

from azure.cli.core.azclierror import InvalidArgumentValueError
from azext_k8s_extension.partner_extensions.EntraWorkloadIAM import (
    EntraWorkloadIAM,
    CONFIG_SETTINGS_USER_TRUST_DOMAIN,
    CONFIG_SETTINGS_USER_LOCAL_AUTHORITY,
    CONFIG_SETTINGS_USER_TENANT_ID,
    CONFIG_SETTINGS_USER_JOIN_TOKEN,
    CONFIG_SETTINGS_HELM_TRUST_DOMAIN,
    CONFIG_SETTINGS_HELM_TENANT_ID,
    CONFIG_SETTINGS_HELM_JOIN_TOKEN
)

from knack.util import CLIError

from unittest.mock import patch

class TestEntraWorkloadIAM(unittest.TestCase):

    def test_workload_iam_create_with_instance_name_too_long(self):
        """
        Test that the checks fail when the user provides an instance name that is too long.
        """

        instance_name = "workload-iam-extra-long-instance-name"

        with self.assertRaises(InvalidArgumentValueError) as context:
            workload_iam = EntraWorkloadIAM()
            workload_iam.Create(cmd=None, client=None, resource_group_name=None,
                cluster_name=None, name=instance_name, cluster_type=None, cluster_rp=None,
                extension_type=None, scope='cluster', auto_upgrade_minor_version=None,
                release_train='dev', version='0.1.0', target_namespace=None,
                release_namespace=None, configuration_settings=None,
                configuration_protected_settings=None, configuration_settings_file=None,
                configuration_protected_settings_file=None, plan_name=None, plan_publisher=None,
                plan_product=None)

        self.assertEqual(str(context.exception),
            f"Name '{instance_name}' is too long, it must be 20 characters long max.")

    def test_workload_iam_create_without_join_token_success(self):
        """
        Test that, when the user doesn't provide a join token, the Create() method calls
        get_join_token() and creates a new one, and that the final configuration settings
        are the expected ones.
        """

        mock_trust_domain_name = 'any_trust_domain_name.com'
        mock_local_authority_name = 'any_local_authority_name'
        mock_tenant_id = 'any_tenant_id'
        mock_join_token = 'any_join_token'

        settings = {
            CONFIG_SETTINGS_USER_TRUST_DOMAIN: mock_trust_domain_name,
            CONFIG_SETTINGS_USER_LOCAL_AUTHORITY: mock_local_authority_name,
            CONFIG_SETTINGS_USER_TENANT_ID: mock_tenant_id,
        }

        def mock_extension_init(_self, *, extension_type, auto_upgrade_minor_version, release_train,
                version, scope, configuration_settings, configuration_protected_settings):
            assert(release_train == "dev")
            assert(configuration_settings[CONFIG_SETTINGS_HELM_JOIN_TOKEN] == mock_join_token);
            assert(configuration_settings[CONFIG_SETTINGS_HELM_TRUST_DOMAIN] == mock_trust_domain_name)
            assert(configuration_settings[CONFIG_SETTINGS_HELM_TENANT_ID] == mock_tenant_id)


        with patch('azext_k8s_extension.partner_extensions.EntraWorkloadIAM.Extension.__init__',
                new=mock_extension_init), \
            patch('azext_k8s_extension.partner_extensions.EntraWorkloadIAM.EntraWorkloadIAM.get_join_token',
                return_value=mock_join_token):

            # Test & assert
            workload_iam = EntraWorkloadIAM()
            _, name, _ = workload_iam.Create(cmd=None, client=None, resource_group_name=None,
                cluster_name=None, name='workload-iam', cluster_type=None, cluster_rp=None,
                extension_type=None, scope='cluster', auto_upgrade_minor_version=None,
                release_train='dev', version='0.1.0', target_namespace=None,
                release_namespace=None, configuration_settings=settings,
                configuration_protected_settings=None, configuration_settings_file=None,
                configuration_protected_settings_file=None, plan_name=None, plan_publisher=None,
                plan_product=None)
            self.assertEqual(name, 'workload-iam')


    def test_workload_iam_create_with_join_token_and_local_authority_success(self):
        """
        Test that, when the user provides a join token, the Create() method doesn't call
        get_join_token(), and that the final configuration settings are the expected ones. The
        provided local authority is only required to generate a new join token. As no token is
        created, the local authority will just be ignored.
        """

        mock_trust_domain_name = 'any_trust_domain_name.com'
        mock_local_authority_name = 'any_local_authority_name'
        mock_tenant_id = 'any_tenant_id'
        mock_join_token = 'any_join_token'

        settings = {
            CONFIG_SETTINGS_USER_TRUST_DOMAIN: mock_trust_domain_name,
            CONFIG_SETTINGS_USER_LOCAL_AUTHORITY: mock_local_authority_name,
            CONFIG_SETTINGS_USER_TENANT_ID: mock_tenant_id,
            CONFIG_SETTINGS_USER_JOIN_TOKEN: mock_join_token,
        }

        def mock_extension_init(_self, *, extension_type, auto_upgrade_minor_version, release_train,
                version, scope, configuration_settings, configuration_protected_settings):
            assert(release_train == "dev")
            assert(configuration_settings[CONFIG_SETTINGS_HELM_JOIN_TOKEN] == mock_join_token);
            assert(configuration_settings[CONFIG_SETTINGS_HELM_TRUST_DOMAIN] == mock_trust_domain_name)
            assert(configuration_settings[CONFIG_SETTINGS_HELM_TENANT_ID] == mock_tenant_id)


        with patch('azext_k8s_extension.partner_extensions.EntraWorkloadIAM.Extension.__init__',
                new=mock_extension_init), \
            patch('azext_k8s_extension.partner_extensions.EntraWorkloadIAM.EntraWorkloadIAM.get_join_token',
                return_value='BAD_JOIN_TOKEN'):

            # Test & assert
            workload_iam = EntraWorkloadIAM()
            _, name, _ = workload_iam.Create(cmd=None, client=None, resource_group_name=None,
                cluster_name=None, name='workload-iam', cluster_type=None, cluster_rp=None,
                extension_type=None, scope='cluster', auto_upgrade_minor_version=None,
                release_train='dev', version='0.1.0', target_namespace=None,
                release_namespace=None, configuration_settings=settings,
                configuration_protected_settings=None, configuration_settings_file=None,
                configuration_protected_settings_file=None, plan_name=None, plan_publisher=None,
                plan_product=None)
            self.assertEqual(name, 'workload-iam')


    def test_workload_iam_create_with_join_token_and_no_local_authority_success(self):
        """
        Test that, when the user provides a join token, the Create() method doesn't call
        get_join_token(), and that the final configuration settings are the expected ones. The
        provided local authority is only required to generate a new join token, so the test should
        pass even without it.
        """

        mock_trust_domain_name = 'any_trust_domain_name.com'
        mock_tenant_id = 'any_tenant_id'
        mock_join_token = 'any_join_token'

        settings = {
            CONFIG_SETTINGS_USER_TRUST_DOMAIN: mock_trust_domain_name,
            CONFIG_SETTINGS_USER_JOIN_TOKEN: mock_join_token,
            CONFIG_SETTINGS_USER_TENANT_ID: mock_tenant_id,
        }

        def mock_extension_init(_self, *, extension_type, auto_upgrade_minor_version, release_train,
                version, scope, configuration_settings, configuration_protected_settings):
            assert(release_train == "dev")
            assert(configuration_settings[CONFIG_SETTINGS_HELM_JOIN_TOKEN] == mock_join_token);
            assert(configuration_settings[CONFIG_SETTINGS_HELM_TRUST_DOMAIN] == mock_trust_domain_name)
            assert(configuration_settings[CONFIG_SETTINGS_HELM_TENANT_ID] == mock_tenant_id)


        with patch('azext_k8s_extension.partner_extensions.EntraWorkloadIAM.Extension.__init__',
                new=mock_extension_init), \
            patch('azext_k8s_extension.partner_extensions.EntraWorkloadIAM.EntraWorkloadIAM.get_join_token',
                return_value='BAD_JOIN_TOKEN'):

            # Test & assert
            workload_iam = EntraWorkloadIAM()
            _, name, _ = workload_iam.Create(cmd=None, client=None, resource_group_name=None,
                cluster_name=None, name='workload-iam', cluster_type=None, cluster_rp=None,
                extension_type=None, scope='cluster', auto_upgrade_minor_version=None,
                release_train='dev', version='0.1.0', target_namespace=None,
                release_namespace=None, configuration_settings=settings,
                configuration_protected_settings=None, configuration_settings_file=None,
                configuration_protected_settings_file=None, plan_name=None, plan_publisher=None,
                plan_product=None)
            self.assertEqual(name, 'workload-iam')

    def test_workload_iam_create_with_trust_domain_local_authority_no_tenant_id(self):
        """
        Test that, when the user doesn't provide a tenant ID, there is an error.
        """

        mock_trust_domain_name = 'any_trust_domain_name.com'
        mock_local_authority_name = 'any_local_authority_name'

        settings = {
            CONFIG_SETTINGS_USER_TRUST_DOMAIN: mock_trust_domain_name,
            CONFIG_SETTINGS_USER_LOCAL_AUTHORITY: mock_local_authority_name,
        }

        with self.assertRaises(InvalidArgumentValueError) as context:
            workload_iam = EntraWorkloadIAM()
            workload_iam.Create(cmd=None, client=None, resource_group_name=None,
                cluster_name=None, name='workload-iam', cluster_type=None, cluster_rp=None,
                extension_type=None, scope='cluster', auto_upgrade_minor_version=None,
                release_train='dev', version='0.1.0', target_namespace=None,
                release_namespace=None, configuration_settings=settings,
                configuration_protected_settings=None, configuration_settings_file=None,
                configuration_protected_settings_file=None, plan_name=None, plan_publisher=None,
                plan_product=None)

        self.assertEqual(str(context.exception),
                f"Invalid configuration settings. Please provide a tenant ID.")

    def test_workload_iam_create_with_wrong_scope_fails(self):
        """
        Test that when the user provides a scope that isn't "cluster" the method Create() fails.
        """

        bad_scope = 'namespace'

        with self.assertRaises(InvalidArgumentValueError) as context:
            workload_iam = EntraWorkloadIAM()
            workload_iam.Create(cmd=None, client=None, resource_group_name=None,
                cluster_name=None, name='workload-iam', cluster_type=None, cluster_rp=None,
                extension_type=None, scope=bad_scope, auto_upgrade_minor_version=None,
                release_train='dev', version='0.1.0', target_namespace=None,
                release_namespace=None, configuration_settings=None,
                configuration_protected_settings=None, configuration_settings_file=None,
                configuration_protected_settings_file=None, plan_name=None, plan_publisher=None,
                plan_product=None)

        self.assertEqual(str(context.exception),
                f"Invalid scope '{bad_scope}'. This extension can only be installed at 'cluster' scope.")


    def test_workload_iam_create_with_not_enough_settings_fails(self):
        """
        Test that when the user doesn't provide the trust domain or local authority the method
        Create() fails.
        """

        mock_trust_domain_name = 'any_trust_domain_name.com'
        mock_local_authority_name = 'any_local_authority_name'
        mock_tenant_id = 'any_tenant_id'

        # Missing local authority

        settings = {
            CONFIG_SETTINGS_USER_TRUST_DOMAIN: mock_trust_domain_name,
            CONFIG_SETTINGS_USER_TENANT_ID: mock_tenant_id,
        }

        with self.assertRaises(InvalidArgumentValueError) as context:
            workload_iam = EntraWorkloadIAM()
            workload_iam.Create(cmd=None, client=None, resource_group_name=None,
                cluster_name=None, name='workload-iam', cluster_type=None, cluster_rp=None,
                extension_type=None, scope='cluster', auto_upgrade_minor_version=None,
                release_train='dev', version='0.1.0', target_namespace=None,
                release_namespace=None, configuration_settings=settings,
                configuration_protected_settings=None, configuration_settings_file=None,
                configuration_protected_settings_file=None, plan_name=None, plan_publisher=None,
                plan_product=None)

        str_settings = str(settings)
        self.assertEqual(str(context.exception),
                f"Invalid configuration settings. Either a join token or a local authority name "
                "must be provided.")

        # Missing trust domain

        settings = {
            CONFIG_SETTINGS_USER_LOCAL_AUTHORITY: mock_local_authority_name,
        }

        with self.assertRaises(InvalidArgumentValueError) as context:
            workload_iam = EntraWorkloadIAM()
            workload_iam.Create(cmd=None, client=None, resource_group_name=None,
                cluster_name=None, name='workload-iam', cluster_type=None, cluster_rp=None,
                extension_type=None, scope='cluster', auto_upgrade_minor_version=None,
                release_train='dev', version='0.1.0', target_namespace=None,
                release_namespace=None, configuration_settings=settings,
                configuration_protected_settings=None, configuration_settings_file=None,
                configuration_protected_settings_file=None, plan_name=None, plan_publisher=None,
                plan_product=None)

        str_settings = str(settings)
        self.assertEqual(str(context.exception),
                f"Invalid configuration settings. Please provide a trust domain name.")

    def test_workload_iam_get_join_token_with_valid_argument_success(self):
        """
        Test that when get_join_token() succeedes it returns a token in the right format (between
        double quotes) and that the arguments passed to "az workload-iam" are the expected ones.
        """

        mock_trust_domain_name = 'any_trust_domain_name.com'
        mock_local_authority_name = 'any_local_authority_name'
        mock_join_token = 'any_join_token'

        class MockCLI():
            def __init__(self):
                pass

            def invoke(self, cmd, out_file):
                class MockResult():
                    def __init__(self):
                        self.result = mock_join_token
                        self.error = None

                self.result = MockResult()

        with patch('azext_k8s_extension.partner_extensions.EntraWorkloadIAM.get_default_cli',
                   return_value=MockCLI()):
            # Test & assert
            workload_iam = EntraWorkloadIAM()
            join_token = workload_iam.get_join_token(mock_trust_domain_name, mock_local_authority_name)
            self.assertEqual(join_token, mock_join_token)


    def test_workload_iam_get_join_token_with_bad_exit_code(self):
        """
        Test that get_join_token() fails with the right error message if "az workload-iam" returns a
        non-zero error code (and if no exception is raised).
        """

        # Set up mocks
        mock_trust_domain_name = 'any_trust_domain_name.com'
        mock_local_authority_name = 'any_local_authority_name'
        mock_join_token = 'any_join_token'

        cmd = [
            "az", "workload-iam", "local-authority", "attestation-method", "create",
            "--td", mock_trust_domain_name,
            "--la", mock_local_authority_name,
            "--type", "joinTokenAttestationMethod",
            "--query", "singleUseToken",
            "--dn", "myJoinToken",
        ]

        class MockCLI():
            def __init__(self):
                pass

            def invoke(self, cmd, out_file):
                class MockResult():
                    def __init__(self):
                        self.result = None
                        self.error = True

                self.result = MockResult()

        with patch('azext_k8s_extension.partner_extensions.EntraWorkloadIAM.get_default_cli',
                   return_value=MockCLI()):
            # Test & assert
            workload_iam = EntraWorkloadIAM()
            cmd_str = " ".join(cmd)
            self.assertRaisesRegex(CLIError,
                f"Error while generating a join token. Command: {cmd_str}",
                workload_iam.get_join_token, mock_trust_domain_name, mock_local_authority_name)
