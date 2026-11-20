# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import unittest
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlsplit

from knack.cli import CLI

from azure.core import PipelineClient
from azure.core.pipeline.policies import ContentDecodePolicy, SansIOHTTPPolicy
from azure.core.pipeline.transport import HttpResponse, HttpTransport
from azure.cli.core.aaz._command_ctx import AAZCommandCtx
from azure.mgmt.resource.resources import ResourceManagementClient

from azext_documentdb.aaz.latest.documentdb.mongocluster import Create, Update
from azext_documentdb.aaz.latest.documentdb.mongocluster.firewall_rule import Create as FirewallRuleCreate
from azext_documentdb.custom import ReplicaPromote, Restore


class _ResourceResponse(HttpResponse):

    def __init__(self, request, resource):
        super().__init__(request, None)
        self.status_code = 200
        self.headers = {"content-type": "application/json"}
        self.content_type = "application/json"
        self._body = json.dumps(resource).encode("utf-8")

    def body(self):
        return self._body

    def stream_download(self, pipeline, **kwargs):
        raise AssertionError("Streaming is not expected for these management requests.")


class StableApiRequestTest(unittest.TestCase):

    _SUBSCRIPTION_ID = "00000000-0000-0000-0000-000000000000"
    _RESOURCE_GROUP_ID = "/subscriptions/" + _SUBSCRIPTION_ID + "/resourceGroups/test-rg"
    _CLUSTER_ID = _RESOURCE_GROUP_ID + "/providers/Microsoft.DocumentDB/mongoClusters/test-cluster"
    _SOURCE_ID = _RESOURCE_GROUP_ID + "/providers/Microsoft.DocumentDB/mongoClusters/source-cluster"
    _IDENTITY_ID = (
        _RESOURCE_GROUP_ID + "/providers/Microsoft.ManagedIdentity/userAssignedIdentities/test-cmk"
    )
    _BASE_URL = "https://management.example.test"

    def _create_command(self, command_type, **command_args):
        command = command_type(cli_ctx=Mock(spec=CLI, enable_color=False))
        with patch("azure.cli.core.aaz._command_ctx.Profile"):
            command.ctx = AAZCommandCtx(
                command.cli_ctx,
                command.get_arguments_schema(),
                {
                    "subscription": self._SUBSCRIPTION_ID,
                    "resource_group": "test-rg",
                    **command_args,
                },
                no_wait_arg="no_wait",
            )
        command.ctx.format_args()
        return command

    def _send_request(self, command, initial_resource=None):
        request_builder = PipelineClient(
            self._BASE_URL,
            transport=Mock(spec=HttpTransport),
            user_agent_policy=SansIOHTTPPolicy(),
        )
        # Keep the real URL, query and JSON encoding; intercept only sending and polling.
        client = Mock(wraps=request_builder)
        responses = []
        if initial_resource is not None:
            responses.append(Mock(
                http_response=Mock(status_code=200),
                context={ContentDecodePolicy.CONTEXT_NAME: initial_resource},
            ))
        responses.append(Mock(http_response=Mock(status_code=202)))
        client.send_request = Mock(side_effect=responses)
        client.build_lro_polling = Mock()
        command.ctx.get_http_client = Mock(return_value=client)

        list(command._execute_operations())

        self.assertEqual(len(responses), client.send_request.call_count)
        request = client.send_request.call_args.kwargs["request"]
        client.send_request.assert_called_with(request=request, stream=False)
        return request, client

    def _assert_request(self, request, method, path):
        url = urlsplit(request.url)
        self.assertEqual(method, request.method)
        self.assertEqual(self._BASE_URL, url.scheme + "://" + url.netloc)
        self.assertEqual(path, url.path)
        self.assertEqual({"api-version": ["2026-09-01"]}, parse_qs(url.query))

    def test_create_request_omits_unspecified_storage_type(self):
        command = self._create_command(
            Create,
            cluster_name="test-cluster",
            location="eastus2",
            admin_user="testadmin",
            admin_password="unit-test-password",
            tier="M30",
            storage_size=128,
            shard_count=1,
            high_availability="Disabled",
        )

        request, _ = self._send_request(command)

        self.assertEqual({
            "location": "eastus2",
            "properties": {
                "administrator": {
                    "userName": "testadmin",
                    "password": "unit-test-password",
                },
                "compute": {"tier": "M30"},
                "storage": {"sizeGb": 128},
                "sharding": {"shardCount": 1},
                "highAvailability": {"targetMode": "Disabled"},
            },
        }, json.loads(request.body))
        self._assert_request(request, "PUT", self._CLUSTER_ID)

    def test_tags_only_update_request_preserves_existing_storage_type(self):
        command = self._create_command(
            Update,
            cluster_name="test-cluster",
            tags={"environment": "after", "owner": "cli"},
        )
        initial_resource = {
            "id": self._CLUSTER_ID,
            "name": "test-cluster",
            "type": "Microsoft.DocumentDB/mongoClusters",
            "location": "eastus2",
            "tags": {"environment": "before"},
            "properties": {
                "provisioningState": "Succeeded",
                "storage": {"sizeGb": 128, "type": "PremiumSSD"},
            },
        }

        request, client = self._send_request(command, initial_resource=initial_resource)

        self.assertEqual({
            "location": "eastus2",
            "tags": {"environment": "after", "owner": "cli"},
            "properties": {
                "storage": {"sizeGb": 128, "type": "PremiumSSD"},
            },
        }, json.loads(request.body))
        get_request = client.send_request.call_args_list[0].kwargs["request"]
        self._assert_request(get_request, "GET", self._CLUSTER_ID)
        self._assert_request(request, "PATCH", self._CLUSTER_ID)

    def test_restore_cmk_request_preserves_omitted_auth_and_target_configuration(self):
        key_url = "https://example.vault.azure.net/keys/documentdb-cmk"
        command = self._create_command(
            Restore,
            cluster_name="test-cluster",
            location="eastus2",
            source_cluster=self._SOURCE_ID,
            restore_time="2026-06-30T10:00:00Z",
            mi_user_assigned=[self._IDENTITY_ID],
            encryption={
                "customer_managed_key_encryption": {
                    "key_encryption_key_identity": {
                        "identity_type": "UserAssignedIdentity",
                        "user_assigned_identity_resource_id": self._IDENTITY_ID,
                    },
                    "key_encryption_key_url": key_url,
                },
            },
            tags={"environment": "restored", "description": "CMK restore"},
            storage_type="PremiumSSDv2",
            public_network_access="Disabled",
        )

        request, _ = self._send_request(command)

        self.assertEqual({
            "identity": {
                "type": "UserAssigned",
                "userAssignedIdentities": {self._IDENTITY_ID: {}},
            },
            "location": "eastus2",
            "tags": {"environment": "restored", "description": "CMK restore"},
            "properties": {
                "createMode": "PointInTimeRestore",
                "restoreParameters": {
                    "sourceResourceId": self._SOURCE_ID,
                    "pointInTimeUTC": "2026-06-30T10:00:00Z",
                },
                "encryption": {
                    "customerManagedKeyEncryption": {
                        "keyEncryptionKeyIdentity": {
                            "identityType": "UserAssignedIdentity",
                            "userAssignedIdentityResourceId": self._IDENTITY_ID,
                        },
                        "keyEncryptionKeyUrl": key_url,
                    },
                },
                "storage": {"type": "PremiumSSDv2"},
                "publicNetworkAccess": "Disabled",
            },
        }, json.loads(request.body))
        self.assertEqual("application/json", request.headers["Content-Type"])
        self._assert_request(request, "PUT", self._CLUSTER_ID)

    def test_planned_promotion_checks_source_then_sends_nested_properties(self):
        command = self._create_command(
            ReplicaPromote,
            name="test-cluster",
            source_cluster="source-cluster",
            mode="Switchover",
            promote_option="Planned",
        )
        transport = Mock(spec=HttpTransport)
        transport.send.side_effect = lambda request, **kwargs: _ResourceResponse(
            request, {"properties": {"replica": {"sourceResourceId": self._SOURCE_ID}}},
        )
        resource_client = ResourceManagementClient(
            Mock(),
            self._SUBSCRIPTION_ID,
            base_url=self._BASE_URL,
            transport=transport,
            authentication_policy=SansIOHTTPPolicy(),
            user_agent_policy=SansIOHTTPPolicy(),
        )

        with patch(
                "azure.cli.core.commands.client_factory.get_mgmt_service_client",
                return_value=resource_client):
            request, client = self._send_request(command)

        transport.send.assert_called_once()
        source_request = transport.send.call_args.args[0]
        self.assertEqual({
            "properties": {"mode": "Switchover", "promoteOption": "Planned"},
        }, json.loads(request.body))
        client.build_lro_polling.assert_called_once()
        polling_call = client.build_lro_polling.call_args
        self.assertEqual({"final-state-via": "location"}, polling_call.kwargs["lro_options"])
        self.assertIsNone(polling_call.args[2](Mock()))
        for current, method, path in (
                (source_request, "GET", self._CLUSTER_ID),
                (request, "POST", self._CLUSTER_ID + "/promote")):
            with self.subTest(method=method):
                self._assert_request(current, method, path)

    def test_firewall_rule_request_preserves_subresource_route_and_ip_range(self):
        command = self._create_command(
            FirewallRuleCreate,
            cluster_name="test-cluster",
            firewall_rule_name="AllowOffice",
            start_ip_address="203.0.113.1",
            end_ip_address="203.0.113.9",
        )

        request, _ = self._send_request(command)

        self.assertEqual({
            "properties": {
                "startIpAddress": "203.0.113.1",
                "endIpAddress": "203.0.113.9",
            },
        }, json.loads(request.body))
        self._assert_request(request, "PUT", self._CLUSTER_ID + "/firewallRules/AllowOffice")


if __name__ == "__main__":
    unittest.main()
