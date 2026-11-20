# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, protected-access
"""Unit tests for Bastion tunnel session token tracking (#10137)."""

import json
import unittest
from unittest import mock

from azext_bastion.tunnel import TunnelServer


def _make_tunnel_server():
    mock_sock = mock.Mock()
    mock_sock.getsockname.return_value = ('127.0.0.1', 59999)
    with mock.patch('azext_bastion.tunnel.socket.socket', return_value=mock_sock):
        return TunnelServer(
            cli_ctx=mock.Mock(),
            local_addr='127.0.0.1',
            local_port=0,
            bastion={'sku': {'name': 'Standard'}},
            bastion_endpoint='test.bastion.azure.com',
            remote_host='/subscriptions/x/resourceGroups/r/providers/Microsoft.Compute/virtualMachines/vm',
            remote_port='22',
        )


class TunnelSessionTokenMintTest(unittest.TestCase):

    @mock.patch('azext_bastion.tunnel.requests.post')
    @mock.patch('azext_bastion.tunnel.Profile')
    def test_each_mint_registers_independent_session_token(self, mock_profile, mock_post):
        mock_profile.return_value.get_raw_token.return_value = ('Bearer', 'aztoken', None)
        mock_post.return_value.status_code = 200

        def _post_response(token_suffix):
            body = mock.Mock()
            body.status_code = 200
            body.content = json.dumps({
                'authToken': f'session-{token_suffix}',
                'nodeId': f'node-{token_suffix}',
                'websocketToken': f'ws-{token_suffix}',
            }).encode('utf-8')
            return body

        mock_post.side_effect = [_post_response(1), _post_response(2)]

        tunnel = _make_tunnel_server()
        ws1, session1, node1 = tunnel._get_auth_token()
        ws2, session2, node2 = tunnel._get_auth_token()

        self.assertEqual(ws1, 'ws-1')
        self.assertEqual(session1, 'session-1')
        self.assertEqual(node1, 'node-1')
        self.assertEqual(ws2, 'ws-2')
        self.assertEqual(session2, 'session-2')
        self.assertEqual(
            tunnel._session_tokens,
            {'session-1': 'node-1', 'session-2': 'node-2'},
        )
        for call in mock_post.call_args_list:
            self.assertIsNone(call.kwargs['data']['token'])


class TunnelSessionTokenDeleteTest(unittest.TestCase):

    @mock.patch('azext_bastion.tunnel.requests.delete')
    def test_successful_delete_removes_token_from_map(self, mock_delete):
        mock_delete.return_value.status_code = 204
        tunnel = _make_tunnel_server()
        tunnel._session_tokens['session-a'] = 'node-a'
        tunnel.last_token = 'session-a'
        tunnel.node_id = 'node-a'

        tunnel._delete_session_token('session-a', 'node-a')

        self.assertNotIn('session-a', tunnel._session_tokens)
        self.assertIsNone(tunnel.last_token)
        mock_delete.assert_called_once()

    @mock.patch('azext_bastion.tunnel.requests.delete')
    def test_404_delete_removes_token_from_map(self, mock_delete):
        mock_delete.return_value.status_code = 404
        tunnel = _make_tunnel_server()
        tunnel._session_tokens['session-b'] = 'node-b'

        tunnel._delete_session_token('session-b', 'node-b')

        self.assertNotIn('session-b', tunnel._session_tokens)

    @mock.patch('azext_bastion.tunnel.requests.delete')
    def test_failed_delete_keeps_token_for_cleanup_retry(self, mock_delete):
        mock_delete.return_value.status_code = 503
        mock_delete.return_value.content = b'busy'
        tunnel = _make_tunnel_server()
        tunnel._session_tokens['session-c'] = 'node-c'

        tunnel._delete_session_token('session-c', 'node-c')

        self.assertIn('session-c', tunnel._session_tokens)
        mock_delete.assert_called_once()


class TunnelSessionCleanupTest(unittest.TestCase):

    @mock.patch.object(TunnelServer, '_delete_session_token_request')
    def test_idle_cleanup_skips_when_connections_active_again(self, mock_delete_req):
        tunnel = _make_tunnel_server()
        tunnel._session_tokens['session-1'] = 'node-1'
        tunnel.active_connections = 1

        tunnel.cleanup(force=False)

        mock_delete_req.assert_not_called()
        self.assertIn('session-1', tunnel._session_tokens)

    @mock.patch.object(TunnelServer, '_delete_session_token_request')
    def test_idle_cleanup_deletes_all_pending_when_no_active_connections(self, mock_delete_req):
        tunnel = _make_tunnel_server()
        tunnel._session_tokens['session-1'] = 'node-1'
        tunnel._session_tokens['session-2'] = 'node-2'
        tunnel.active_connections = 0

        tunnel.cleanup(force=False)

        self.assertEqual(mock_delete_req.call_count, 2)
        self.assertEqual(tunnel._session_tokens, {})

    @mock.patch.object(TunnelServer, '_delete_session_token_request')
    def test_forced_cleanup_deletes_even_with_active_connections(self, mock_delete_req):
        tunnel = _make_tunnel_server()
        tunnel._session_tokens['session-1'] = 'node-1'
        tunnel.active_connections = 3

        tunnel.cleanup(force=True)

        mock_delete_req.assert_called_once()
        self.assertEqual(tunnel._session_tokens, {})


if __name__ == '__main__':
    unittest.main()
