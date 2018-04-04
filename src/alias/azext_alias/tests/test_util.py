# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

import unittest

from azext_alias.util import remove_pos_arg_placeholders

class TestUtil(unittest.TestCase):

    def test_remove_pos_arg_placeholders(self):
        self.assertEqual('webapp create', remove_pos_arg_placeholders('webapp create'))

    def test_remove_pos_arg_placeholders_with_pos_arg(self):
        self.assertEqual('network dns', remove_pos_arg_placeholders('network dns {{ arg_1 }}'))

    def test_remove_pos_arg_placeholders_with_args(self):
        self.assertEqual('vm create', remove_pos_arg_placeholders('vm create -g test -n test'))

    def test_remove_pos_arg_placeholders_with_query(self):
        self.assertEqual('group list', remove_pos_arg_placeholders('group list --query "[].{Name:name, Location:location}" --output table'))


if __name__ == '__main__':
    unittest.main()
