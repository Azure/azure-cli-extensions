#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest

from service_name import _get_uncovered_commands


class TestServiceName(unittest.TestCase):

    def test_top_level_command_covers_nested_commands(self):
        extension_commands = {'containerapp create', 'containerapp show'}

        uncovered = _get_uncovered_commands(extension_commands, {'containerapp'})

        self.assertEqual(uncovered, set())

    def test_nested_command_covers_only_its_namespace(self):
        extension_commands = {'aro hcp cluster create', 'aro hcp get-versions', 'aro create'}

        uncovered = _get_uncovered_commands(extension_commands, {'aro hcp'})

        self.assertEqual(uncovered, {'aro create'})

    def test_command_prefix_must_end_on_token_boundary(self):
        extension_commands = {'aro hcp2 cluster create'}

        uncovered = _get_uncovered_commands(extension_commands, {'aro hcp'})

        self.assertEqual(uncovered, extension_commands)

    def test_exact_command_is_covered(self):
        extension_commands = {'aro hcp'}

        uncovered = _get_uncovered_commands(extension_commands, {'aro hcp'})

        self.assertEqual(uncovered, set())


if __name__ == '__main__':
    unittest.main()