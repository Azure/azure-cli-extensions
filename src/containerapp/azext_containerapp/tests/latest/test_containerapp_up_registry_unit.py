# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest import mock

from azure.cli.core.azclierror import ValidationError

from azext_containerapp import _up_utils


class TestContainerappUpRegistryDetails(unittest.TestCase):

    def setUp(self):
        patcher = mock.patch.multiple(
            _up_utils,
            _set_acr_creds=mock.DEFAULT,
            _get_acr_rg=mock.DEFAULT,
            ResourceGroup=mock.DEFAULT,
            AzureContainerRegistry=mock.DEFAULT,
        )
        self.mocks = patcher.start()
        self.addCleanup(patcher.stop)
        self.cmd = mock.Mock()
        self.cmd.cli_ctx.cloud.suffixes.acr_login_server_endpoint = ".azurecr.io"
        self.app = mock.Mock(registry_user=None, registry_pass=None)

    def test_missing_credentials_use_acr_name(self):
        for server, suffix, source in (
                ("myacr.azurecr.io", ".azurecr.io", None),
                ("myacr.azurecr.io", ".azurecr.io", "."),
                ("MyAcr.AzureCR.io", ".azurecr.io", None),
                ("https://myacr.azurecr.io", ".azurecr.io", None),
                ("https://myacr.azurecr.io", ".azurecr.io", "."),
                ("https://myacr.azurecr.io/", ".azurecr.io", None),
                ("https://myacr.azurecr.io/", ".azurecr.io", "."),
                ("https://MyAcr.AzureCR.io/", ".azurecr.io", None),
                ("myacr.azurecr.cn", ".azurecr.cn", None)):
            for username, password in ((None, None), ("user", None), (None, "password")):
                with self.subTest(server=server, source=source, username=username, password=password):
                    self.mocks["_set_acr_creds"].reset_mock()
                    self.app.registry_server = server
                    self.app.registry_user = username
                    self.app.registry_pass = password
                    self.cmd.cli_ctx.cloud.suffixes.acr_login_server_endpoint = suffix

                    _up_utils._get_registry_details(self.cmd, self.app, source)

                    self.mocks["_set_acr_creds"].assert_called_once_with(self.cmd, self.app, "myacr")
                    self.assertEqual("myacr", self.mocks["AzureContainerRegistry"].call_args.args[0])
                    self.assertEqual(server, self.app.registry_server)
        self.mocks["_get_acr_rg"].assert_not_called()

    def test_missing_credentials_reject_non_acr_servers(self):
        for server in ("myacr.example.com", "myacr.azurecr.io.example.com", "a.b.azurecr.io", "docker.io"):
            for username, password in ((None, None), ("user", None), (None, "password")):
                with self.subTest(server=server, username=username, password=password):
                    self.app.registry_server = server
                    self.app.registry_user = username
                    self.app.registry_pass = password

                    with self.assertRaises(ValidationError) as error:
                        _up_utils._get_registry_details(self.cmd, self.app, None)

                    self.assertEqual(
                        f"Registry server '{server}' is not an Azure Container Registry. Use "
                        "--registry-server, or pass --registry-username and --registry-password.",
                        str(error.exception),
                    )
        self.mocks["_set_acr_creds"].assert_not_called()
        self.mocks["_get_acr_rg"].assert_not_called()

    def test_missing_credentials_validate_with_source(self):
        for server in ("myacr.azurecr.io.example.com", "a.b.azurecr.io"):
            with self.subTest(server=server):
                self.app.registry_server = server
                with self.assertRaises(ValidationError) as error:
                    _up_utils._get_registry_details(self.cmd, self.app, ".")
                self.assertEqual(
                    f"Registry server '{server}' is not an Azure Container Registry. Use "
                    "--registry-server, or pass --registry-username and --registry-password.",
                    str(error.exception),
                )
        self.mocks["_set_acr_creds"].assert_not_called()
        self.mocks["_get_acr_rg"].assert_not_called()

    def test_explicit_credentials_preserve_registry_handling(self):
        self.app.registry_user = "user"
        self.app.registry_pass = "password"
        for server in ("docker.io", "ghcr.io", "myacr.azurecr.io"):
            with self.subTest(server=server):
                self.mocks["_get_acr_rg"].reset_mock()
                self.app.registry_server = server

                _up_utils._get_registry_details(self.cmd, self.app, None)

                self.mocks["_get_acr_rg"].assert_called_once_with(self.app)
                self.assertEqual(server.split(".")[0], self.mocks["AzureContainerRegistry"].call_args.args[0])
                self.assertEqual(server, self.app.registry_server)
        self.mocks["_set_acr_creds"].assert_not_called()

    def test_source_preserves_existing_registry_guard(self):
        for server, suffix in (
                ("docker.io", ".azurecr.io"),
                ("ghcr.io", ".azurecr.io"),
                ("MyAcr.AzureCR.io", ".azurecr.io"),
                ("myacr.azurecr.cn", ".azurecr.cn")):
            for username, password in ((None, None), ("user", "password")):
                with self.subTest(server=server, username=username, password=password):
                    self.app.registry_server = server
                    self.app.registry_user = username
                    self.app.registry_pass = password
                    self.cmd.cli_ctx.cloud.suffixes.acr_login_server_endpoint = suffix

                    with self.assertRaises(ValidationError) as error:
                        _up_utils._get_registry_details(self.cmd, self.app, ".")

                    self.assertEqual("Cannot supply non-Azure registry when using --source.", str(error.exception))
        self.mocks["_set_acr_creds"].assert_not_called()
        self.mocks["_get_acr_rg"].assert_not_called()
