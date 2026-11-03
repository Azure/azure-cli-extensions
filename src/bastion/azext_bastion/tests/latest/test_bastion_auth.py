# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from threading import Lock
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock, patch

import requests
from azure.core.exceptions import HttpResponseError
from knack.util import CLIError

from azext_bastion.custom import _get_tunnel, rdp_bastion_host
from azext_bastion.developer_sku_helper import _get_data_pod
from azext_bastion.tunnel import TunnelServer


BASTION_SUBSCRIPTION = "11111111-1111-1111-1111-111111111111"
TARGET_SUBSCRIPTION = "22222222-2222-2222-2222-222222222222"
BASTION_ID = (
    f"/subscriptions/{BASTION_SUBSCRIPTION}/resourceGroups/bastion-rg"
    "/providers/Microsoft.Network/bastionHosts/test-bastion"
)
TARGET_ID = (
    f"/subscriptions/{TARGET_SUBSCRIPTION}/resourceGroups/vm-rg"
    "/providers/Microsoft.Compute/virtualMachines/test-vm"
)


def response(status_code, content):
    result = requests.Response()
    result.status_code = status_code
    result._content = content
    return result


class BastionAuthTest(TestCase):
    def setUp(self):
        self.cli_ctx = Mock()
        self.cli_ctx.data = {"subscription_id": TARGET_SUBSCRIPTION}
        self.cmd = SimpleNamespace(cli_ctx=self.cli_ctx)
        self.bastion = {
            "id": BASTION_ID,
            "dnsName": "bastion.example",
            "sku": {"name": "Standard"},
            "enableTunneling": True,
        }
        self.profile_patch = patch("azure.cli.core._profile.Profile")
        self.profile = self.profile_patch.start()
        self.addCleanup(self.profile_patch.stop)
        tunnel_profile_patch = patch("azext_bastion.tunnel.Profile", self.profile)
        tunnel_profile_patch.start()
        self.addCleanup(tunnel_profile_patch.stop)
        self.profile.return_value.get_raw_token.return_value = (
            ("Bearer", "scoped-token", {"accessToken": "scoped-token"}),
            BASTION_SUBSCRIPTION,
            "bastion-tenant",
        )

    def assert_scoped_token(self):
        self.profile.assert_called_with(cli_ctx=self.cli_ctx)
        self.profile.return_value.get_raw_token.assert_called_with(
            subscription=BASTION_SUBSCRIPTION
        )

    def make_tunnel(self):
        tunnel = object.__new__(TunnelServer)
        tunnel.cli_ctx = self.cli_ctx
        tunnel.bastion = self.bastion
        tunnel.bastion_endpoint = "bastion.example"
        tunnel.remote_host = TARGET_ID
        tunnel.remote_port = 22
        tunnel.last_token = None
        tunnel.node_id = None
        tunnel.host_name = None
        tunnel.connection_lock = Lock()
        tunnel.active_connections = 1
        return tunnel

    @patch("azext_bastion.tunnel.TunnelServer")
    def test_token_uses_subscription_from_bastion_arm_id(self, server):
        self.assertIs(
            _get_tunnel(self.cmd, self.bastion, "bastion.example", TARGET_ID, 22),
            server.return_value
        )
        self.assert_scoped_token()
        self.assertEqual(self.cli_ctx.data["subscription_id"], TARGET_SUBSCRIPTION)

    @patch("azext_bastion.tunnel.TunnelServer")
    def test_same_subscription_still_requests_scoped_token(self, _server):
        self.cli_ctx.data["subscription_id"] = BASTION_SUBSCRIPTION
        _get_tunnel(self.cmd, self.bastion, "bastion.example", TARGET_ID, 22)
        self.assert_scoped_token()

    @patch("azext_bastion.tunnel.TunnelServer")
    def test_no_default_subscription_is_required(self, _server):
        self.cli_ctx.data.clear()
        _get_tunnel(self.cmd, self.bastion, "bastion.example", TARGET_ID, 22)
        self.assert_scoped_token()
        self.assertEqual(self.cli_ctx.data, {})

    def test_missing_subscription_credentials_are_not_masked(self):
        self.profile.return_value.get_raw_token.side_effect = CLIError("Please log in")
        with self.assertRaisesRegex(CLIError, "Please log in"):
            self.make_tunnel()._get_auth_token()

    @patch("azext_bastion.tunnel.requests.post")
    def test_tunnel_uses_bastion_subscription_not_target_subscription(self, post):
        post.return_value = response(
            200, b'{"authToken":"session","nodeId":"node","websocketToken":"websocket"}'
        )
        tunnel = self.make_tunnel()
        self.assertEqual(tunnel._get_auth_token(), "websocket")
        self.assert_scoped_token()
        content = post.call_args.kwargs["data"]
        self.assertEqual(content["aztoken"], "scoped-token")
        self.assertEqual(content["resourceId"], TARGET_ID)
        self.assertEqual(tunnel.last_token, "session")
        self.assertEqual(tunnel.node_id, "node")

    @patch("azext_bastion.tunnel.requests.post")
    def test_ip_connect_token_uses_bastion_subscription(self, post):
        post.return_value = response(
            200, b'{"authToken":"session","nodeId":"node","websocketToken":"websocket"}'
        )
        tunnel = self.make_tunnel()
        tunnel.remote_host = (
            f"/subscriptions/{BASTION_SUBSCRIPTION}/resourceGroups/bastion-rg"
            "/providers/Microsoft.Network/bh-hostConnect/10.0.0.4"
        )
        tunnel.set_host_name("10.0.0.4")
        tunnel._get_auth_token()
        self.assert_scoped_token()
        self.assertEqual(post.call_args.kwargs["data"]["hostname"], "10.0.0.4")

    @patch("azext_bastion.tunnel.requests.post")
    def test_token_is_reacquired_for_subsequent_connections(self, post):
        post.return_value = response(
            200, b'{"authToken":"session","nodeId":"node","websocketToken":"websocket"}'
        )
        tunnel = self.make_tunnel()
        tunnel._get_auth_token()
        tunnel._get_auth_token()
        self.assertEqual(self.profile.return_value.get_raw_token.call_count, 2)
        self.assert_scoped_token()
        self.assertEqual(post.call_args.kwargs["headers"], {"X-Node-Id": "node"})

    @patch("azext_bastion.tunnel.requests.post")
    def test_auth_errors_preserve_http_status_and_service_message(self, post):
        for status in (401, 403):
            with self.subTest(status=status):
                post.return_value = response(status, b'{"message":"Access denied"}')
                with self.assertRaisesRegex(HttpResponseError, f"HTTP {status}.*Access denied"):
                    self.make_tunnel()._get_auth_token()

    @patch("azext_bastion.tunnel.requests.post")
    def test_non_json_auth_error_reports_http_status(self, post):
        post.return_value = response(401, b"Unauthorized")
        with self.assertRaisesRegex(HttpResponseError, "HTTP 401"):
            self.make_tunnel()._get_auth_token()

    @patch("azext_bastion.tunnel.logger.error")
    def test_auth_failure_closes_client_and_logs_error(self, log_error):
        tunnel = self.make_tunnel()
        tunnel._get_auth_token = Mock(side_effect=CLIError("Please log in"))
        client = Mock()
        tunnel._handle_client(client, 0)
        client.close.assert_called_once()
        log_error.assert_called_once()
        self.assertEqual(tunnel.active_connections, 0)

    @patch("azext_bastion.tunnel.TunnelServer")
    def test_credentials_are_checked_before_creating_tunnel(self, server):
        self.profile.return_value.get_raw_token.side_effect = CLIError("Please log in")
        with self.assertRaisesRegex(CLIError, "Please log in"):
            _get_tunnel(self.cmd, self.bastion, "bastion.example", TARGET_ID, 22)
        server.assert_not_called()
        self.assert_scoped_token()

    @patch("requests.post")
    def test_developer_connection_uses_bastion_subscription(self, post):
        post.return_value = response(200, b"pod.example")
        self.assertEqual(_get_data_pod(self.cmd, 22, TARGET_ID, self.bastion), "pod.example")
        self.assert_scoped_token()
        self.assertEqual(post.call_args.kwargs["json"]["azToken"], "scoped-token")

    @patch("requests.post")
    def test_developer_connection_rejects_auth_error_as_endpoint(self, post):
        post.return_value = response(403, b"Forbidden")
        with self.assertRaisesRegex(HttpResponseError, "HTTP 403"):
            _get_data_pod(self.cmd, 22, TARGET_ID, self.bastion)

    @patch("azext_bastion.custom._write_to_file")
    @patch("azext_bastion.custom._get_rdp_path", return_value="mstsc")
    @patch("azext_bastion.custom.platform.system", return_value="Windows")
    @patch("azext_bastion.custom.requests.get")
    @patch("azext_bastion.aaz.latest.network.bastion.Show")
    def test_gateway_rdp_uses_bastion_subscription(self, show, get, _system, _path, _write):
        show.return_value.return_value = self.bastion
        get.return_value = response(200, b"rdp file")
        process_helper = SimpleNamespace(launch_and_wait=Mock())
        with patch.dict("sys.modules", {"azext_bastion._process_helper": process_helper}):
            rdp_bastion_host(self.cmd, TARGET_ID, None, "bastion-rg", "test-bastion")
        self.assert_scoped_token()
        self.assertIn("scoped-token", get.call_args.kwargs["headers"]["Authorization"])
