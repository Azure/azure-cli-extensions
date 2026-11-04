# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest.mock import Mock, patch

from azext_storage_mover.custom import endpoint_create_for_s3_with_hmac


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
