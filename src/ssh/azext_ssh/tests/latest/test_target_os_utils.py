# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest import mock

from azext_ssh import target_os_utils


class TargetOSUtilsTest(unittest.TestCase):

    @mock.patch('azext_ssh.aaz.latest.hybrid_compute.machine.Show')
    def test_get_arc_os(self, mock_get_arc):
        cmd = mock.Mock()
        cmd.cli_ctx = mock.Mock()

        showclass = mock.Mock()
        showclass.return_value = {
            "properties": {
                "osType": "os_type",
                "agentVersion": "arc_agent_version"
            }
        }

        mock_get_arc.return_value = showclass

        os, agent = target_os_utils._get_arc_server_os(cmd, "rg", "vm")

        self.assertEqual(os, "os_type")
        self.assertEqual(agent, "arc_agent_version")

    @mock.patch('azext_ssh.aaz.latest.hybrid_compute.machine.Show', autospec=True)
    def test_get_arc_os_exception(self, mock_get_arc):
        cmd = mock.Mock()
        cmd.cli_ctx = mock.Mock()

        mock_get_arc.return_value.side_effect = mock.Mock(side_effect=Exception('Test'))

        os, agent = target_os_utils._get_arc_server_os(cmd, "rg", "vm")

        self.assertEqual(os, None)
        self.assertEqual(agent, None)

    @mock.patch('azext_ssh.aaz.latest.connected_v_mwarev_sphere.virtual_machine.Show')
    def test_get_vmware_os(self, mock_get_vmware):
        cmd = mock.Mock()
        cmd.cli_ctx = mock.Mock()

        showclass = mock.Mock()
        showclass.return_value = {
            "osProfile": {
                "osType": "os_type"
            },
            "properties": {
                "guestAgentProfile": {
                    "agentVersion": "agent_version"
                }
            }
        }

        mock_get_vmware.return_value = showclass

        os, agent = target_os_utils._get_connected_vmware_os(cmd, "rg", "vm")

        self.assertEqual(os, "os_type")
        self.assertEqual(agent, "agent_version")

    @mock.patch('azext_ssh.aaz.latest.connected_v_mwarev_sphere.virtual_machine.Show', autospec=True)
    def test_get_vmware_os_exception(self, mock_get_vmware):
        cmd = mock.Mock()
        cmd.cli_ctx = mock.Mock()

        mock_get_vmware.return_value.side_effect = mock.Mock(side_effect=Exception('Test'))

        os, agent = target_os_utils._get_connected_vmware_os(cmd, "rg", "vm")

        self.assertEqual(os, None)
        self.assertEqual(agent, None)


if __name__ == '__main__':
    unittest.main()
