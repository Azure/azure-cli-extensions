# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from copy import deepcopy
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from azure.cli.core.aaz._command_ctx import AAZCommandCtx
from azure.core.pipeline.policies import ContentDecodePolicy

from azext_storage_discovery.aaz.latest.storage_discovery.workspace import Create, List, Show


class StorageDiscoveryFeaturesTest(unittest.TestCase):
    subscription = "00000000-0000-0000-0000-000000000000"

    def setUp(self):
        self.client = Mock()
        self.client.format_url.side_effect = lambda template, **kwargs: template.format(**kwargs)
        self.capabilities = {
            "azureBlobStorage": {
                "capacityDetails": {"status": "Enabled"},
                "prefixConfigurations": [{
                    "storageAccountName": "accountone",
                    "containerName": "containerone",
                    "prefix": "logs/",
                }],
            },
        }
        self.workspace = {
            "name": "testworkspace",
            "location": "francecentral",
            "properties": {
                "capabilities": deepcopy(self.capabilities),
                "sku": "Standard",
                "workspaceRoots": [f"/subscriptions/{self.subscription}"],
                "scopes": [{
                    "displayName": "testscope",
                    "resourceTypes": ["Microsoft.Storage/storageAccounts"],
                }],
            },
        }

    def command(self, command_type, **arguments):
        with patch("azure.cli.core.aaz._command_ctx.Profile"):
            ctx = AAZCommandCtx(
                cli_ctx=Mock(),
                schema=command_type.get_arguments_schema(),
                command_args={"subscription": self.subscription, **arguments},
            )
        ctx.format_args()
        ctx.get_http_client = Mock(return_value=self.client)
        command = command_type.__new__(command_type)
        command.ctx = ctx
        command.callbacks = {}
        return command

    @staticmethod
    def session(body, status=200):
        return SimpleNamespace(
            http_response=SimpleNamespace(status_code=status),
            context={ContentDecodePolicy.CONTEXT_NAME: deepcopy(body)},
        )

    def assert_request(self, method, path, content=None):
        arguments = self.client._request.call_args.args
        self.assertEqual(arguments[0], method)
        self.assertEqual(arguments[1], path)
        self.assertEqual(arguments[2], {"api-version": "2026-10-01-preview"})
        self.assertEqual(arguments[4], content)

    @property
    def workspace_path(self):
        return (
            f"/subscriptions/{self.subscription}/resourceGroups/testrg/providers/"
            "Microsoft.StorageDiscovery/storageDiscoveryWorkspaces/testworkspace"
        )

    def test_create_serializes_capabilities_and_returns_them(self):
        command = self.command(
            Create,
            resource_group="testrg",
            storage_discovery_workspace_name="testworkspace",
            location="francecentral",
            sku="Standard",
            workspace_roots=[f"/subscriptions/{self.subscription}"],
            scopes=[{
                "display_name": "testscope",
                "resource_types": ["Microsoft.Storage/storageAccounts"],
            }],
            capabilities={
                "azure_blob_storage": {
                    "capacity_details": {"status": "Enabled"},
                    "prefix_configurations": [{
                        "storage_account_name": "accountone",
                        "container_name": "containerone",
                        "prefix": "logs/",
                    }],
                },
            },
        )
        self.client.send_request.return_value = self.session(self.workspace, status=201)
        command._execute_operations()
        expected = deepcopy(self.workspace)
        del expected["name"]
        self.assert_request("PUT", self.workspace_path, expected)
        self.assertEqual(command._output()["properties"]["capabilities"], self.capabilities)

    def test_show_returns_capabilities(self):
        command = self.command(Show, resource_group="testrg", storage_discovery_workspace_name="testworkspace")
        self.client.send_request.return_value = self.session(self.workspace)
        command._execute_operations()
        self.assert_request("GET", self.workspace_path)
        self.assertEqual(command._output()["properties"]["capabilities"], self.capabilities)

    def test_workspace_list_returns_capabilities_at_both_scopes(self):
        for resource_group in (None, "testrg"):
            with self.subTest(resource_group=resource_group):
                arguments = {"resource_group": resource_group} if resource_group else {}
                command = self.command(List, **arguments)
                self.client.send_request.return_value = self.session({"value": [self.workspace]})
                command._execute_operations()
                scope = f"/resourceGroups/{resource_group}" if resource_group else ""
                self.assert_request(
                    "GET",
                    f"/subscriptions/{self.subscription}{scope}/providers/"
                    "Microsoft.StorageDiscovery/storageDiscoveryWorkspaces",
                )
                values, _ = command._output()
                self.assertEqual(values[0]["properties"]["capabilities"], self.capabilities)
