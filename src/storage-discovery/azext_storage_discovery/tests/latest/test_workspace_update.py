# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from copy import deepcopy
import shlex
import unittest
from unittest.mock import MagicMock, patch

from azure.cli.core.aaz import AAZHttpOperation
from azure.cli.core.aaz._command_ctx import AAZCommandCtx
from azure.cli.core import get_default_cli

from azext_storage_discovery import StorageDiscoveryCommandsLoader
from azext_storage_discovery.aaz.latest.storage_discovery.workspace import Update as GeneratedWorkspaceUpdate
from azext_storage_discovery.custom import WorkspaceUpdate


class WorkspaceUpdateTest(unittest.TestCase):
    def setUp(self):
        self.workspace = {
            "location": "francecentral",
            "tags": {"environment": "test"},
            "properties": {
                "description": "original",
                "sku": "Standard",
                "workspaceRoots": ["/subscriptions/00000000-0000-0000-0000-000000000000"],
                "scopes": [{
                    "displayName": "testscope",
                    "resourceTypes": ["Microsoft.Storage/storageAccounts"],
                }],
                "capabilities": {
                    "azureBlobStorage": {
                        "capacityDetails": {"status": "Enabled"},
                        "prefixConfigurations": [{
                            "storageAccountName": "accountone",
                            "containerName": "containerone",
                            "prefix": "old/",
                        }],
                    },
                },
            },
        }

    def update_content(self, **arguments):
        with patch("azure.cli.core.aaz._command_ctx.Profile"):
            ctx = AAZCommandCtx(
                cli_ctx=MagicMock(),
                schema=WorkspaceUpdate._build_arguments_schema(),
                command_args={
                    "resource_group": "testrg",
                    "storage_discovery_workspace_name": "testworkspace",
                    **arguments,
                },
            )
        ctx.format_args()
        ctx.set_var(
            "instance",
            deepcopy(self.workspace),
            schema_builder=WorkspaceUpdate.StorageDiscoveryWorkspacesGet._build_schema_on_200,
        )
        command = WorkspaceUpdate.__new__(WorkspaceUpdate)
        command.ctx = ctx
        command.pre_instance_update(ctx.vars.instance)
        command.InstanceUpdateByJson(ctx)()
        return AAZHttpOperation.serialize_content(ctx.vars.instance)

    def test_status_update_preserves_prefix_configurations(self):
        content = self.update_content(
            capabilities={"azure_blob_storage": {"capacity_details": {"status": "Disabled"}}},
        )
        blob_storage = content["properties"]["capabilities"]["azureBlobStorage"]
        self.assertEqual(blob_storage["capacityDetails"]["status"], "Disabled")
        self.assertEqual(
            blob_storage["prefixConfigurations"],
            self.workspace["properties"]["capabilities"]["azureBlobStorage"]["prefixConfigurations"],
        )
        self.assertEqual(content["tags"], self.workspace["tags"])
        self.assertEqual(content["properties"]["scopes"], self.workspace["properties"]["scopes"])

    def test_prefix_update_preserves_capacity_details(self):
        content = self.update_content(
            capabilities={"azure_blob_storage": {"prefix_configurations": [{
                "storage_account_name": "accounttwo",
                "container_name": "containertwo",
                "prefix": "new/",
            }]}},
        )
        blob_storage = content["properties"]["capabilities"]["azureBlobStorage"]
        self.assertEqual(blob_storage["capacityDetails"], {"status": "Enabled"})
        self.assertEqual(blob_storage["prefixConfigurations"], [{
            "storageAccountName": "accounttwo",
            "containerName": "containertwo",
            "prefix": "new/",
        }])

    def test_prefix_clear_preserves_capacity_details(self):
        for clear_value in ([], None):
            with self.subTest(clear_value=clear_value):
                content = self.update_content(
                    capabilities={"azure_blob_storage": {"prefix_configurations": clear_value}},
                )
                blob_storage = content["properties"]["capabilities"]["azureBlobStorage"]
                if clear_value is None:
                    self.assertNotIn("prefixConfigurations", blob_storage)
                else:
                    self.assertEqual(blob_storage["prefixConfigurations"], clear_value)
                self.assertEqual(blob_storage["capacityDetails"], {"status": "Enabled"})

    def test_capabilities_can_be_cleared(self):
        content = self.update_content(capabilities=None)
        self.assertNotIn("capabilities", content["properties"])

    def test_unrelated_update_preserves_capabilities(self):
        content = self.update_content(description="updated")
        self.assertEqual(content["properties"]["description"], "updated")
        self.assertEqual(
            content["properties"]["capabilities"],
            self.workspace["properties"]["capabilities"],
        )

    def test_capabilities_can_be_added(self):
        del self.workspace["properties"]["capabilities"]
        content = self.update_content(
            capabilities={"azure_blob_storage": {"capacity_details": {"status": "Enabled"}}},
        )
        self.assertEqual(content["properties"]["capabilities"], {
            "azureBlobStorage": {"capacityDetails": {"status": "Enabled"}},
        })

    def test_missing_status_for_new_capabilities_is_rejected(self):
        del self.workspace["properties"]["capabilities"]
        with self.assertRaisesRegex(ValueError, "Missing a required field in request content: status"):
            self.update_content(capabilities={"azure_blob_storage": {"prefix_configurations": []}})

    def test_custom_update_is_registered(self):
        loader = StorageDiscoveryCommandsLoader(cli_ctx=get_default_cli())
        loader.load_command_table([])
        self.assertIsInstance(
            loader.command_table["storage-discovery workspace update"],
            WorkspaceUpdate,
        )

    def test_update_example_quotes_description(self):
        examples = [
            line.strip() for line in GeneratedWorkspaceUpdate.__doc__.splitlines()
            if line.strip().startswith("az storage-discovery workspace update")
        ]
        self.assertTrue(examples)
        arguments = shlex.split(examples[0])
        self.assertEqual(
            arguments[arguments.index("--description") + 1],
            "Sample Storage Discovery Workspace",
        )
