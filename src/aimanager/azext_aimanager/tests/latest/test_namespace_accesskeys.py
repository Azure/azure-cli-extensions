# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest.mock import MagicMock

from azext_aimanager import custom


class MockCmd:
    pass


class TestNamespaceAccessKeys(unittest.TestCase):

    def setUp(self):
        self.cmd = MockCmd()
        self.client = MagicMock()

    def test_list_accesskeys(self):
        self.client.list_access_keys.return_value = "access-info"

        result = custom.aimanager_namespace_list_accesskeys(
            self.cmd, self.client, "rg", "manager", "namespace")

        self.assertEqual(result, "access-info")
        self.client.list_access_keys.assert_called_once_with(
            "rg", "manager", "namespace", headers={})

    def test_rotate_accesskeys(self):
        self.client.rotate_keys.return_value = "rotated"

        result = custom.aimanager_namespace_rotate_accesskeys(
            self.cmd, self.client, "rg", "manager", "namespace")

        self.assertEqual(result, "rotated")
        self.client.rotate_keys.assert_called_once_with(
            "rg", "manager", "namespace", headers={})

    def test_custom_headers_are_forwarded(self):
        custom.aimanager_namespace_list_accesskeys(
            self.cmd, self.client, "rg", "manager", "namespace",
            aks_custom_headers="a=1,b=2")

        self.client.list_access_keys.assert_called_once_with(
            "rg", "manager", "namespace", headers={"a": "1", "b": "2"})


if __name__ == '__main__':
    unittest.main()
