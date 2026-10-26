# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import importlib
import inspect
import json
import pkgutil
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlparse

from azure.cli.core.aaz import AAZCommand, AAZWaitCommand
from azure.cli.core.commands import client_factory
from azure.cli.core.mock import DummyCli
from azure.core.pipeline.policies import ContentDecodePolicy
from azext_storage_mover import custom
from azext_storage_mover.aaz.latest import storage_mover
from azext_storage_mover.aaz.latest.storage_mover.connection import (
    Create as ConnectionCreate, Update as ConnectionUpdate,
)
from azext_storage_mover.aaz.latest.storage_mover.endpoint import (
    Create as EndpointCreate, Update as EndpointUpdate,
)
from azext_storage_mover.aaz.latest.storage_mover.job_definition import (
    Create as JobDefinitionCreate, ReconcileJob, Update as JobDefinitionUpdate,
)
from azext_storage_mover.custom import endpoint_create_for_s3_with_hmac


SUBSCRIPTION_ID = "00000000-0000-0000-0000-000000000000"
STORAGE_ACCOUNT_ID = (
    f"/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/resource-group"
    "/providers/Microsoft.Storage/storageAccounts/account"
)
PARTNER_STORAGE_ACCOUNT_ID = (
    "/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/partner"
    "/providers/Microsoft.Storage/storageAccounts/partner"
)
PARTNER_ENDPOINT_ID = (
    "/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/partner"
    "/providers/Microsoft.StorageMover/storageMovers/partner/endpoints/target"
)


class StorageMoverRecordingProcessorTest(unittest.TestCase):

    def test_tenant_is_sanitized_in_body_and_operation_identifier(self):
        from azext_storage_mover.tests.latest.test_storage_mover import StorageMoverTenantIdReplacer
        tenant_id = "11111111-1111-1111-1111-111111111111"
        replacement = "00000000-0000-0000-0000-000000000000"
        processor = StorageMoverTenantIdReplacer()
        processor.register_name_pair(tenant_id, replacement)
        response = processor.process_response({
            "headers": {
                "content-type": ["application/json"],
                "x-ms-operation-identifier": ["tenantId=" + tenant_id + ",objectId=principal"],
            },
            "body": {"string": json.dumps({"tenantId": tenant_id})},
        })
        self.assertEqual(json.loads(response["body"]["string"])["tenantId"], replacement)
        self.assertEqual(
            response["headers"]["x-ms-operation-identifier"],
            ["tenantId=" + replacement + ",objectId=principal"],
        )


class StorageMoverEndpointCustomTest(unittest.TestCase):

    @patch("azext_storage_mover.custom.Create")
    def test_s3_with_hmac_create_assigns_system_identity(self, create_class):
        cmd = Mock()
        create_command = create_class.return_value

        endpoint_create_for_s3_with_hmac(
            cmd,
            "endpoint",
            "resource-group",
            "storage-mover",
            "https://s3.example.com/bucket",
            "MINIO",
            "https://vault.vault.azure.net/secrets/access-key",
            "https://vault.vault.azure.net/secrets/secret-key",
        )

        create_class.assert_called_once_with(cmd.loader)
        create_command.assert_called_once()
        args = create_command.call_args.args[0]
        self.assertEqual(args["mi_system_assigned"], "True")

    def test_cross_tenant_endpoint_create_parameters(self):
        for function, properties, required in [
            (custom.endpoint_create_for_storage_container, "azure_storage_blob_container",
             {"blob_container_name": "container", "storage_account_resource_id": STORAGE_ACCOUNT_ID}),
            (custom.endpoint_create_for_storage_smb_file_share, "azure_storage_smb_file_share",
             {"file_share_name": "share", "storage_account_resource_id": STORAGE_ACCOUNT_ID}),
        ]:
            with self.subTest(function=function.__name__), patch(
                "azext_storage_mover.custom.Create"
            ) as create_class:
                function(
                    Mock(), "endpoint", "resource-group", "storage-mover",
                    enable_cross_tenant_transfer=True,
                    allowed_storage_accounts=[PARTNER_STORAGE_ACCOUNT_ID], **required,
                )
                args = create_class.return_value.call_args.args[0]
                self.assertTrue(args[properties]["enable_cross_tenant_transfer"])
                self.assertEqual(args[properties]["allowed_storage_accounts"], [PARTNER_STORAGE_ACCOUNT_ID])
                if properties == "azure_storage_blob_container":
                    self.assertEqual(args["mi_system_assigned"], "True")

    def test_cross_tenant_endpoint_update_clears_settings(self):
        for function, properties in [
            (custom.endpoint_update_for_storage_container, "azure_storage_blob_container"),
            (custom.endpoint_update_for_storage_smb_file_share, "azure_storage_smb_file_share"),
        ]:
            with self.subTest(function=function.__name__), patch(
                "azext_storage_mover.custom.Update"
            ) as update_class:
                function(
                    Mock(), "endpoint", "resource-group", "storage-mover",
                    enable_cross_tenant_transfer=False, allowed_storage_accounts=[],
                )
                args = update_class.return_value.call_args.args[0]
                self.assertIs(args[properties]["enable_cross_tenant_transfer"], False)
                self.assertEqual(args[properties]["allowed_storage_accounts"], [])

    def test_cross_tenant_endpoint_update_omits_unspecified_settings(self):
        for function, properties in [
            (custom.endpoint_update_for_storage_container, "azure_storage_blob_container"),
            (custom.endpoint_update_for_storage_smb_file_share, "azure_storage_smb_file_share"),
        ]:
            with self.subTest(function=function.__name__), patch(
                "azext_storage_mover.custom.Update"
            ) as update_class:
                function(Mock(), "endpoint", "resource-group", "storage-mover", description="updated")
                args = update_class.return_value.call_args.args[0]
                self.assertNotIn("enable_cross_tenant_transfer", args[properties])
                self.assertNotIn("allowed_storage_accounts", args[properties])

    def test_fsx_endpoint_parameters(self):
        for function, operation, properties, source_type, required in [
            (custom.endpoint_create_for_nfs, "Create", "nfs_mount", "FSX-EFS",
             {"export": "/export", "host": "nfs.example.com", "nfs_version": "NFSv4_1"}),
            (custom.endpoint_update_for_nfs, "Update", "nfs_mount", "FSX-EFS", {}),
            (custom.endpoint_create_for_smb, "Create", "smb_mount", "FSX-SMB",
             {"host": "smb.example.com", "share_name": "share"}),
            (custom.endpoint_update_for_smb, "Update", "smb_mount", "FSX-SMB", {}),
        ]:
            with self.subTest(function=function.__name__), patch(
                "azext_storage_mover.custom." + operation
            ) as command_class:
                function(
                    Mock(), "endpoint", "resource-group", "storage-mover",
                    source_type=source_type, **required,
                )
                args = command_class.return_value.call_args.args[0]
                self.assertEqual(args[properties]["source_type"], source_type)
                if "nfs_version" in required:
                    self.assertEqual(args[properties]["nfs_version"], "NFSv4_1")


class StorageMoverApiContractTest(unittest.TestCase):

    def _invoke(self, command_class, args, responses):
        command = command_class(cli_ctx=DummyCli())
        AAZCommand._handler(command, dict(args, subscription=SUBSCRIPTION_ID))
        with patch.object(command.ctx, "get_login_credential", return_value=Mock()):
            client = command.ctx.get_http_client("MgmtClient")
        sessions = [
            SimpleNamespace(
                http_response=Mock(status_code=200),
                context={ContentDecodePolicy.CONTEXT_NAME: response},
            )
            for response in responses
        ]
        with patch.object(client, "send_request", side_effect=sessions) as send:
            command._execute_operations()
            output = command._output()
        self.assertEqual(send.call_count, len(responses))
        requests = [call.kwargs["request"] for call in send.call_args_list]
        for request in requests:
            self.assertEqual(parse_qs(urlparse(request.url).query)["api-version"], ["2026-05-01"])
        return requests, output

    def test_invocation_uses_cli_client_configuration(self):
        with patch.object(
            client_factory, "_prepare_client_kwargs_track2",
            wraps=client_factory._prepare_client_kwargs_track2,
        ) as prepare:
            self._invoke(
                ReconcileJob,
                {
                    "job_definition_name": "job", "resource_group": "resource-group",
                    "storage_mover_name": "storage-mover", "project_name": "project",
                },
                [{"jobRunResourceId": "job-run-resource-id"}],
            )
        prepare.assert_called_once()

    def test_cross_tenant_endpoint_create_serialization(self):
        for argument, endpoint_type, required in [
            ("azure_storage_blob_container", "AzureStorageBlobContainer", {"blob_container_name": "container"}),
            ("azure_storage_smb_file_share", "AzureStorageSmbFileShare", {"file_share_name": "share"}),
        ]:
            with self.subTest(endpoint_type=endpoint_type):
                requests, output = self._invoke(
                    EndpointCreate,
                    {
                        "endpoint_name": "endpoint", "resource_group": "resource-group",
                        "storage_mover_name": "storage-mover", "mi_system_assigned": "True",
                        argument: dict(
                            required, storage_account_resource_id=STORAGE_ACCOUNT_ID,
                            enable_cross_tenant_transfer=True,
                            allowed_storage_accounts=[PARTNER_STORAGE_ACCOUNT_ID],
                        ),
                    },
                    [{"properties": {
                        "endpointType": endpoint_type, "enableCrossTenantTransfer": True,
                        "allowedStorageAccounts": [PARTNER_STORAGE_ACCOUNT_ID],
                    }}],
                )
                body = json.loads(requests[0].body)
                self.assertEqual(requests[0].method, "PUT")
                self.assertEqual(body["identity"], {"type": "SystemAssigned"})
                self.assertEqual(body["properties"]["endpointType"], endpoint_type)
                self.assertIs(body["properties"]["enableCrossTenantTransfer"], True)
                self.assertEqual(body["properties"]["allowedStorageAccounts"], [PARTNER_STORAGE_ACCOUNT_ID])
                self.assertEqual(output["properties"]["allowedStorageAccounts"], [PARTNER_STORAGE_ACCOUNT_ID])

    def test_cross_tenant_endpoint_update_replaces_allow_list(self):
        for argument, endpoint_type in [
            ("azure_storage_blob_container", "AzureStorageBlobContainer"),
            ("azure_storage_smb_file_share", "AzureStorageSmbFileShare"),
        ]:
            for allowed_accounts in [[PARTNER_STORAGE_ACCOUNT_ID], []]:
                with self.subTest(endpoint_type=endpoint_type, allowed_accounts=allowed_accounts):
                    existing = {
                        "identity": {"type": "SystemAssigned"},
                        "properties": {
                            "endpointType": endpoint_type, "enableCrossTenantTransfer": True,
                            "allowedStorageAccounts": [STORAGE_ACCOUNT_ID],
                            "storageAccountResourceId": STORAGE_ACCOUNT_ID,
                            **({"blobContainerName": "container"} if endpoint_type == "AzureStorageBlobContainer"
                               else {"fileShareName": "share"}),
                        },
                    }
                    requests, _ = self._invoke(
                        EndpointUpdate,
                        {
                            "endpoint_name": "endpoint", "resource_group": "resource-group",
                            "storage_mover_name": "storage-mover",
                            argument: {
                                "enable_cross_tenant_transfer": False,
                                "allowed_storage_accounts": allowed_accounts,
                            },
                        },
                        [existing, existing],
                    )
                    body = json.loads(requests[-1].body)
                    self.assertEqual([request.method for request in requests], ["GET", "PUT"])
                    self.assertIs(body["properties"]["enableCrossTenantTransfer"], False)
                    self.assertEqual(body["properties"]["allowedStorageAccounts"], allowed_accounts)

    def test_endpoint_update_preserves_omitted_cross_tenant_settings(self):
        for endpoint_type in ["AzureStorageBlobContainer", "AzureStorageSmbFileShare"]:
            with self.subTest(endpoint_type=endpoint_type):
                existing = {
                    "identity": {"type": "SystemAssigned"},
                    "properties": {
                        "endpointType": endpoint_type, "enableCrossTenantTransfer": True,
                        "allowedStorageAccounts": [PARTNER_STORAGE_ACCOUNT_ID],
                        "storageAccountResourceId": STORAGE_ACCOUNT_ID,
                        **({"blobContainerName": "container"} if endpoint_type == "AzureStorageBlobContainer"
                           else {"fileShareName": "share"}),
                    },
                }
                requests, _ = self._invoke(
                    EndpointUpdate,
                    {
                        "endpoint_name": "endpoint", "resource_group": "resource-group",
                        "storage_mover_name": "storage-mover", "description": "updated",
                    },
                    [existing, existing],
                )
                properties = json.loads(requests[-1].body)["properties"]
                self.assertIs(properties["enableCrossTenantTransfer"], True)
                self.assertEqual(properties["allowedStorageAccounts"], [PARTNER_STORAGE_ACCOUNT_ID])
                self.assertEqual(properties["description"], "updated")

    def test_fsx_and_nfs_version_serialization(self):
        for argument, endpoint_type, source_type, settings in [
            ("nfs_mount", "NfsMount", "FSX-EFS",
             {"host": "nfs.example.com", "export": "/export", "nfs_version": "NFSv4_1"}),
            ("smb_mount", "SmbMount", "FSX-SMB", {"host": "smb.example.com", "share_name": "share"}),
        ]:
            with self.subTest(endpoint_type=endpoint_type):
                requests, _ = self._invoke(
                    EndpointCreate,
                    {
                        "endpoint_name": "endpoint", "resource_group": "resource-group",
                        "storage_mover_name": "storage-mover",
                        argument: dict(settings, source_type=source_type),
                    },
                    [{"properties": {"endpointType": endpoint_type, "sourceType": source_type}}],
                )
                properties = json.loads(requests[0].body)["properties"]
                self.assertEqual(properties["sourceType"], source_type)
                if endpoint_type == "NfsMount":
                    self.assertEqual(properties["nfsVersion"], "NFSv4_1")

    def test_smb_credential_updates_preserve_discriminator(self):
        existing = {
            "properties": {
                "endpointType": "SmbMount", "host": "smb.example.com", "shareName": "share",
                "credentials": {
                    "type": "AzureKeyVaultSmb",
                    "usernameUri": "https://vault.vault.azure.net/secrets/username",
                    "passwordUri": "https://vault.vault.azure.net/secrets/password",
                },
            },
        }
        for username, password in [
            ("", ""),
            ("https://vault.vault.azure.net/secrets/new-username",
             "https://vault.vault.azure.net/secrets/new-password"),
        ]:
            with self.subTest(username=username):
                requests, _ = self._invoke(
                    EndpointUpdate,
                    {
                        "endpoint_name": "endpoint", "resource_group": "resource-group",
                        "storage_mover_name": "storage-mover",
                        "smb_mount": {"credentials": {"username_uri": username, "password_uri": password}},
                    },
                    [existing, existing],
                )
                credentials = json.loads(requests[-1].body)["properties"]["credentials"]
                self.assertEqual(credentials, {
                    "type": "AzureKeyVaultSmb", "usernameUri": username, "passwordUri": password,
                })

    def test_job_definition_create_new_fields(self):
        properties = {
            "copyMode": "Additive", "sourceName": "source", "targetName": "target",
            "jobType": "CloudToCloud", "isCrossTenantJob": True,
            "crossTenantEndpointTenantId": "11111111-1111-1111-1111-111111111111",
            "crossTenantEndpointResourceId": PARTNER_ENDPOINT_ID,
            "syncMode": "FullScan", "moverSyncedUntil": "2026-05-01T00:00:00.000Z",
            "schedule": {"frequency": "Hourly", "repeatInterval": "1h", "isActive": True},
        }
        requests, output = self._invoke(
            JobDefinitionCreate,
            {
                "job_definition_name": "job", "resource_group": "resource-group",
                "storage_mover_name": "storage-mover", "project_name": "project",
                "copy_mode": "Additive", "source_name": "source", "target_name": "target",
                "job_type": "CloudToCloud", "is_cross_tenant_job": True,
                "cross_tenant_endpoint_tenant_id": properties["crossTenantEndpointTenantId"],
                "cross_tenant_endpoint_resource_id": PARTNER_ENDPOINT_ID,
                "sync_mode": "FullScan", "mover_synced_until": "2026-05-01T00:00:00Z",
                "schedule": {"frequency": "Hourly", "repeat_interval": "1h", "is_active": True},
            },
            [{"properties": properties}],
        )
        body = json.loads(requests[0].body)["properties"]
        for name, value in properties.items():
            self.assertEqual(body[name], value)
            self.assertEqual(output[name], value)

    def test_agentless_job_definition_serialization(self):
        connection_id = (
            f"/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/resource-group/providers"
            "/Microsoft.StorageMover/storageMovers/storage-mover/connections/connection"
        )
        requests, _ = self._invoke(
            JobDefinitionCreate,
            {
                "job_definition_name": "job", "resource_group": "resource-group",
                "storage_mover_name": "storage-mover", "project_name": "project",
                "copy_mode": "Additive", "source_name": "source", "target_name": "target",
                "job_type": "OnPremToCloudAgentLess", "connections": [connection_id],
            },
            [{"properties": {"jobType": "OnPremToCloudAgentLess", "connections": [connection_id]}}],
        )
        properties = json.loads(requests[0].body)["properties"]
        self.assertEqual(properties["jobType"], "OnPremToCloudAgentLess")
        self.assertEqual(properties["connections"], [connection_id])

    def test_job_definition_update_preserves_create_only_fields(self):
        existing = {
            "properties": {
                "copyMode": "Additive", "sourceName": "source", "targetName": "target",
                "jobType": "CloudToCloud", "isCrossTenantJob": True,
                "crossTenantEndpointTenantId": "11111111-1111-1111-1111-111111111111",
                "crossTenantEndpointResourceId": PARTNER_ENDPOINT_ID,
            },
        }
        requests, _ = self._invoke(
            JobDefinitionUpdate,
            {
                "job_definition_name": "job", "resource_group": "resource-group",
                "storage_mover_name": "storage-mover", "project_name": "project",
                "sync_mode": "SnapshotBased", "mover_synced_until": "2026-05-01T00:00:00Z",
                "schedule": {"frequency": "Hourly", "repeat_interval": "1h"},
            },
            [existing, existing],
        )
        properties = json.loads(requests[-1].body)["properties"]
        self.assertEqual(properties["syncMode"], "SnapshotBased")
        self.assertEqual(properties["moverSyncedUntil"], "2026-05-01T00:00:00.000Z")
        self.assertEqual(properties["schedule"], {"frequency": "Hourly", "repeatInterval": "1h"})
        for name, value in existing["properties"].items():
            self.assertEqual(properties[name], value)
        schema = JobDefinitionUpdate.get_arguments_schema()
        for name in ["is_cross_tenant_job", "cross_tenant_endpoint_tenant_id", "cross_tenant_endpoint_resource_id"]:
            self.assertNotIn(name, schema._fields)

    def test_reconcile_job_posts_without_body(self):
        response = {"jobRunResourceId": "job-run-resource-id"}
        requests, output = self._invoke(
            ReconcileJob,
            {
                "job_definition_name": "job", "resource_group": "resource-group",
                "storage_mover_name": "storage-mover", "project_name": "project",
            },
            [response],
        )
        self.assertEqual(requests[0].method, "POST")
        self.assertTrue(urlparse(requests[0].url).path.endswith("/jobDefinitions/job/reconcileJob"))
        self.assertIsNone(requests[0].body)
        self.assertEqual(output, response)
        self.assertFalse(ReconcileJob.AZ_SUPPORT_NO_WAIT)

    def test_existing_argument_aliases(self):
        for command_class in [ConnectionCreate, ConnectionUpdate]:
            with self.subTest(command=command_class):
                self.assertIn("--pls-id", command_class.get_arguments_schema().private_link_service_id._options)
        for command_class in [JobDefinitionCreate, JobDefinitionUpdate]:
            with self.subTest(command=command_class):
                self.assertIn("--data-validation",
                              command_class.get_arguments_schema().data_integrity_validation._options)

    def test_all_generated_commands_use_may_api(self):
        commands = set()
        for module_info in pkgutil.walk_packages(storage_mover.__path__, storage_mover.__name__ + "."):
            module = importlib.import_module(module_info.name)
            for command_class in vars(module).values():
                if (inspect.isclass(command_class) and issubclass(command_class, AAZCommand)
                        and command_class.__module__ == module_info.name):
                    commands.add(command_class)
                    with self.subTest(command=command_class):
                        if not issubclass(command_class, AAZWaitCommand):
                            self.assertEqual(command_class._aaz_info["version"], "2026-05-01")
                        for resource in command_class._aaz_info["resources"]:
                            self.assertEqual(resource[2], "2026-05-01")
        self.assertIn(ReconcileJob, commands)
