# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest.mock import Mock

from vcr.request import Request

from azure.cli.core import get_default_cli
from azure.cli.core.aaz._command_ctx import AAZCommandCtx
from azure.cli.core.azclierror import InvalidArgumentValueError

from azext_documentdb.custom import Restore
from azext_documentdb.tests.latest.test_documentdb import MongoClusterOperationTokenReplacer


class RestoreTest(unittest.TestCase):

    _SUBSCRIPTION_ID = "00000000-0000-0000-0000-000000000000"
    _SOURCE_ID = (
        "/subscriptions/00000000-0000-0000-0000-000000000000/"
        "resourceGroups/source-rg/providers/Microsoft.DocumentDB/"
        "mongoClusters/source-cluster"
    )
    _IDENTITY_ID = (
        "/subscriptions/00000000-0000-0000-0000-000000000000/"
        "resourceGroups/identity-rg/providers/Microsoft.ManagedIdentity/"
        "userAssignedIdentities/documentdb-cmk"
    )
    _KEY_URL = "https://example.vault.azure.net/keys/documentdb-cmk"

    def _create_command(self, **overrides):
        command_args = {
            "subscription": self._SUBSCRIPTION_ID,
            "resource_group": "restore-rg",
            "cluster_name": "restored-cluster",
            "location": "eastus2",
            "source_cluster": self._SOURCE_ID,
            "restore_time": "2026-06-30T10:00:00Z",
            **overrides,
        }
        command = Restore(cli_ctx=get_default_cli())
        command.ctx = AAZCommandCtx(
            command.cli_ctx,
            command.get_arguments_schema(),
            command_args,
            no_wait_arg="no_wait",
        )
        command.ctx.format_args()
        return command

    def _serialize_content(self, command):
        command.pre_operations()
        command.ctx.get_http_client = Mock(return_value=Mock())
        operation = command.MongoClustersCreateOrUpdate(ctx=command.ctx)
        return operation.content

    def _cmk_encryption(self, identity_id=None):
        return {
            "customer_managed_key_encryption": {
                "key_encryption_key_identity": {
                    "identity_type": "UserAssignedIdentity",
                    "user_assigned_identity_resource_id": (
                        identity_id or self._IDENTITY_ID
                    ),
                },
                "key_encryption_key_url": self._KEY_URL,
            }
        }

    def test_legacy_native_auth_payload_is_unchanged(self):
        content = self._serialize_content(self._create_command(
            admin_user="dbadmin",
            admin_password="P@ssword123!",
        ))

        self.assertEqual({
            "location": "eastus2",
            "properties": {
                "administrator": {
                    "password": "P@ssword123!",
                    "userName": "dbadmin",
                },
                "createMode": "PointInTimeRestore",
                "restoreParameters": {
                    "pointInTimeUTC": "2026-06-30T10:00:00Z",
                    "sourceResourceId": self._SOURCE_ID,
                },
            },
        }, content)

    def test_entra_only_payload_omits_administrator(self):
        content = self._serialize_content(self._create_command(
            auth_allowed_modes=["MicrosoftEntraID"],
        ))

        self.assertNotIn("administrator", content["properties"])
        self.assertEqual(
            ["MicrosoftEntraID"],
            content["properties"]["authConfig"]["allowedModes"],
        )

    def test_dual_auth_payload_includes_administrator(self):
        content = self._serialize_content(self._create_command(
            admin_user="dbadmin",
            admin_password="P@ssword123!",
            auth_allowed_modes=["NativeAuth", "MicrosoftEntraID"],
        ))

        self.assertEqual(
            ["NativeAuth", "MicrosoftEntraID"],
            content["properties"]["authConfig"]["allowedModes"],
        )
        self.assertEqual(
            "dbadmin",
            content["properties"]["administrator"]["userName"],
        )

    def test_native_auth_requires_administrator_credentials(self):
        command = self._create_command(auth_allowed_modes=["NativeAuth"])

        with self.assertRaisesRegex(
                InvalidArgumentValueError, "required when NativeAuth is enabled"):
            command.pre_operations()

    def test_legacy_restore_requires_administrator_credentials(self):
        command = self._create_command()

        with self.assertRaisesRegex(
                InvalidArgumentValueError, "auth-allowed-modes and --encryption are omitted"):
            command.pre_operations()

    def test_administrator_credentials_must_be_provided_together(self):
        command = self._create_command(admin_user="dbadmin")

        with self.assertRaisesRegex(
                InvalidArgumentValueError, "must be provided together"):
            command.pre_operations()

    def test_entra_only_rejects_administrator_credentials(self):
        command = self._create_command(
            admin_user="dbadmin",
            admin_password="P@ssword123!",
            auth_allowed_modes=["MicrosoftEntraID"],
        )

        with self.assertRaisesRegex(
                InvalidArgumentValueError, "cannot be used"):
            command.pre_operations()

    def test_authentication_modes_reject_duplicate_values(self):
        command = self._create_command(
            auth_allowed_modes=["MicrosoftEntraID", "MicrosoftEntraID"],
        )

        with self.assertRaisesRegex(
                InvalidArgumentValueError, "must not contain duplicate values"):
            command.pre_operations()

    def test_authentication_modes_reject_empty_list(self):
        command = self._create_command(auth_allowed_modes=[])

        with self.assertRaisesRegex(
                InvalidArgumentValueError, "must contain at least one"):
            command.pre_operations()

    def test_cmk_payload_includes_matching_user_assigned_identity(self):
        content = self._serialize_content(self._create_command(
            mi_user_assigned=[self._IDENTITY_ID],
            encryption=self._cmk_encryption(),
        ))

        self.assertNotIn("administrator", content["properties"])
        self.assertNotIn("authConfig", content["properties"])
        self.assertEqual("UserAssigned", content["identity"]["type"])
        self.assertIn(
            self._IDENTITY_ID,
            content["identity"]["userAssignedIdentities"],
        )
        cmk = content["properties"]["encryption"]["customerManagedKeyEncryption"]
        self.assertEqual(self._KEY_URL, cmk["keyEncryptionKeyUrl"])
        self.assertEqual(
            self._IDENTITY_ID,
            cmk["keyEncryptionKeyIdentity"]["userAssignedIdentityResourceId"],
        )

    def test_cmk_native_auth_payload_includes_administrator(self):
        content = self._serialize_content(self._create_command(
            admin_user="dbadmin",
            admin_password="P@ssword123!",
            mi_user_assigned=[self._IDENTITY_ID],
            encryption=self._cmk_encryption(),
        ))

        self.assertEqual(
            {"userName": "dbadmin", "password": "P@ssword123!"},
            content["properties"]["administrator"],
        )
        self.assertNotIn("authConfig", content["properties"])
        self.assertEqual("UserAssigned", content["identity"]["type"])
        self.assertIn(self._IDENTITY_ID, content["identity"]["userAssignedIdentities"])
        cmk = content["properties"]["encryption"]["customerManagedKeyEncryption"]
        self.assertEqual(self._KEY_URL, cmk["keyEncryptionKeyUrl"])
        self.assertEqual(
            self._IDENTITY_ID,
            cmk["keyEncryptionKeyIdentity"]["userAssignedIdentityResourceId"],
        )

    def test_cmk_identity_must_be_assigned_to_cluster(self):
        command = self._create_command(
            admin_user="dbadmin",
            admin_password="P@ssword123!",
            mi_user_assigned=["/subscriptions/example/identity/other"],
            encryption=self._cmk_encryption(),
        )

        with self.assertRaisesRegex(
                InvalidArgumentValueError, "must also be supplied"):
            command.pre_operations()

    def test_cmk_requires_complete_encryption_configuration(self):
        command = self._create_command(
            admin_user="dbadmin",
            admin_password="P@ssword123!",
            mi_user_assigned=[self._IDENTITY_ID],
            encryption={
                "customer_managed_key_encryption": {
                    "key_encryption_key_identity": {
                        "identity_type": "UserAssignedIdentity",
                        "user_assigned_identity_resource_id": self._IDENTITY_ID,
                    },
                }
            },
        )

        with self.assertRaisesRegex(
                InvalidArgumentValueError, "key-encryption-key-url"):
            command.pre_operations()


class OperationTokenReplacerTest(unittest.TestCase):

    _URL = (
        "https://management.example.test/subscriptions/example/providers/"
        "Microsoft.DocumentDB/locations/example/mongoClusterAzureAsyncOperation/op"
        "?api-version=2026-06-15-preview&t=timestamp&c=encrypted%2Bvalue&s=signature&h=hash"
    )
    _SANITIZED_URL = (
        "https://management.example.test/subscriptions/example/providers/"
        "Microsoft.DocumentDB/locations/example/mongoClusterAzureAsyncOperation/op"
        "?api-version=2026-06-15-preview&t=REDACTED&c=REDACTED&s=REDACTED&h=REDACTED"
    )

    def test_request_tokens_are_redacted_without_changing_operation_or_api(self):
        processor = MongoClusterOperationTokenReplacer()
        request = Request("GET", self._URL, None, {})
        self.assertEqual(self._SANITIZED_URL, processor.process_request(request).uri)

    def test_response_headers_and_echoed_body_url_are_redacted(self):
        processor = MongoClusterOperationTokenReplacer()
        response = {
            "headers": {
                "Azure-AsyncOperation": [self._URL],
                "Location": [self._URL],
                "content-type": ["application/json"],
            },
            "body": {"string": '{"name": "' + self._URL + '"}'},
        }
        result = processor.process_response(response)
        self.assertEqual([self._SANITIZED_URL], result["headers"]["Azure-AsyncOperation"])
        self.assertEqual([self._SANITIZED_URL], result["headers"]["Location"])
        self.assertEqual(
            '{"name": "' + self._SANITIZED_URL + '"}', result["body"]["string"],
        )

    def test_previously_registered_request_url_is_redacted_in_response_body(self):
        processor = MongoClusterOperationTokenReplacer()
        processor.process_request(Request("GET", self._URL, None, {}))
        response = {
            "headers": {"content-type": ["application/json"]},
            "body": {"string": '{"name": "' + self._URL + '"}'},
        }
        self.assertEqual(
            '{"name": "' + self._SANITIZED_URL + '"}',
            processor.process_response(response)["body"]["string"],
        )

    def test_other_endpoints_and_already_sanitized_urls_are_unchanged(self):
        for url in (
                self._URL.replace("/mongoClusterAzureAsyncOperation/", "/otherOperation/"),
                self._SANITIZED_URL):
            with self.subTest(url=url):
                processor = MongoClusterOperationTokenReplacer()
                self.assertEqual(url, processor.process_request(Request("GET", url, None, {})).uri)
                self.assertEqual([], processor.names_name)


if __name__ == "__main__":
    unittest.main()
