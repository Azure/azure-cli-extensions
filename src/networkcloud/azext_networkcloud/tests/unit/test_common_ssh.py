# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# flake8: noqa

import unittest
from abc import ABC
from unittest import mock

from azext_networkcloud.operations.common_ssh import CustomSshOptions
from azure.cli.core.aaz._base import AAZUndefined
from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.cli.core.commands import AzCliCommand
from azure.cli.core.mock import DummyCli
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


class TestCommonSsh(unittest.TestCase):
    """TestCommonSsh provides common methods to validate ssh
    operations in CommonSsh like generate ssh key, read sshkey from path,etc"""

    def validate_generate_ssh_keys(self, mock_expand_user, mock_keys):
        # Mock user home dir path
        mock_expand_user.assert_called_with = "~"
        test_home_dir = "/home/user"
        mock_expand_user.return_value = test_home_dir

        # Mock generated keys return values
        test_key_contents = "======ssh-rsa foo"
        mock_keys.return_value = test_key_contents

        # Call func
        result = CustomSshOptions.generate_ssh_keys()

        # Validate call values match mock home dir
        mock_keys.assert_called_with(
            "{}/.ssh/id_rsa_generated".format(test_home_dir),
            "{}/.ssh/id_rsa_generated.pub".format(test_home_dir),
        )

        # Validate result matches key returned by azcli lib
        self.assertEqual(result, [{"keyData": test_key_contents}])

    def validate_get_ssh_keys_from_path(self, mock_isfile, mock_isdir, mock_listdir):
        key = rsa.generate_private_key(65537, 2048)
        valid_key = str(
            key.public_key().public_bytes(
                serialization.Encoding.OpenSSH, serialization.PublicFormat.OpenSSH
            ),
            "UTF-8",
        )
        invalid_key = "==== ssh-rsa"

        # Create a list of paths
        paths = ["/home/user/.ssh/id_rsa.pub", "/home/user2/.ssh/id_rsa.pub"]
        mock_listdir.return_value = ["/dir/key.pub", "/dir/id_rsa.pub"]

        # Test that a path that is not a dir nor a file raises exception
        mock_isdir.return_value = False
        mock_isfile.return_value = False
        with self.assertRaises(InvalidArgumentValueError):
            CustomSshOptions.get_ssh_keys_from_path(paths)

        # Test that a valid file path to a valid key results in a list of keys
        mock_isfile.return_value = True
        with mock.patch("builtins.open", mock.mock_open(None, valid_key)):
            result = CustomSshOptions.get_ssh_keys_from_path(paths)
            self.assertEqual([{"keyData": valid_key} for _ in paths], result)

        # Test that a valid file path to a invalid key raises exception
        with mock.patch("builtins.open", mock.mock_open(None, invalid_key)):
            with self.assertRaises(InvalidArgumentValueError):
                CustomSshOptions.get_ssh_keys_from_path(paths)

        # Test that a valid dir path to valid keys results in a list of keys
        mock_isdir.return_value = True
        mock_isfile.return_value = False
        with mock.patch("builtins.open", mock.mock_open(None, valid_key)):
            result = CustomSshOptions.get_ssh_keys_from_path(paths)
            self.assertEqual([{"keyData": valid_key} for _ in range(4)], result)

        # Test that a valid dir path to invalid keys raises exception
        with mock.patch("builtins.open", mock.mock_open(None, invalid_key)):
            with self.assertRaises(InvalidArgumentValueError):
                CustomSshOptions.get_ssh_keys_from_path(paths)

        # Test that a valid dir path with no keys raises exception
        mock_listdir.return_value = []
        with self.assertRaises(InvalidArgumentValueError):
            CustomSshOptions.get_ssh_keys_from_path(paths)

        # Test that a valid dir path with no .pub files raises exception
        mock_listdir.return_value = ["/home/user/.ssh/id_rsa"]
        with self.assertRaises(InvalidArgumentValueError):
            CustomSshOptions.get_ssh_keys_from_path(paths)

    def validate_add_key_action(self):
        # Generate some valid public keys for testing
        keys = []
        for _ in range(5):
            key = rsa.generate_private_key(65537, 2048)
            pub = key.public_key().public_bytes(
                serialization.Encoding.OpenSSH, serialization.PublicFormat.OpenSSH
            )
            # Convert from bytes
            keys.append(str(pub, "UTF-8"))

        # Wrap keys in expected return format
        expected_result = [{"keyData": x} for x in keys]

        # TODO(drewwalters): a future enhancement would be to figure out how to
        # pass keys wrapped in the type the code expects. Passing as a string
        # achieves the same result for now. Example:
        # values = [AAZStrType(x) for x in keys]
        self.assertEqual(expected_result, CustomSshOptions.add_ssh_key_action(keys))

        # Change a key to an invalid type and validate it raises exception
        keys[1] = "==== ssh-rsa invalid-key"
        with self.assertRaises(InvalidArgumentValueError):
            CustomSshOptions.add_ssh_key_action(keys)
