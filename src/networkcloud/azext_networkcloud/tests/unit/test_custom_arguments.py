# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# flake8: noqa

import os
import unittest
from unittest import mock

from azext_networkcloud.operations.custom_arguments import AAZFileStringArgFormat
from azure.cli.core import azclierror
from azure.cli.core.aaz import AAZArgumentsSchema, AAZObjectArg, AAZStrArg
from azure.cli.core.aaz._command_ctx import AAZCommandCtx
from azure.cli.core.mock import DummyCli
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


class TestAAZFileStringArgFormat(unittest.TestCase):
    @staticmethod
    def format_arg(schema, data):
        ctx = AAZCommandCtx(cli_ctx=DummyCli(), schema=schema, command_args=data)
        ctx.format_args()
        return ctx.args

    def test_ssh_key_fmt(self):
        schema = AAZArgumentsSchema()
        schema.ssh_public_key = AAZObjectArg(
            fmt=AAZFileStringArgFormat(), nullable=True
        )
        key = rsa.generate_private_key(65537, 2048)
        valid_key = str(
            key.public_key().public_bytes(
                serialization.Encoding.OpenSSH, serialization.PublicFormat.OpenSSH
            ),
            "UTF-8",
        )
        invalid_key = "==== ssh-rsa"

        # Empty value for ssh key
        schema.ssh_public_key.key_data = AAZStrArg()
        with self.assertRaises(azclierror.InvalidArgumentValueError):
            self.format_arg(schema, {"ssh_public_key": {"key_data": ""}})

        # Test invalid ssh key raises exception
        with self.assertRaises(azclierror.InvalidArgumentValueError):
            self.format_arg(schema, {"ssh_public_key": {"key_data": invalid_key}})

        # Test that a path that is not a valid file raises exception
        with self.assertRaises(azclierror.InvalidArgumentValueError):
            self.format_arg(
                schema, {"ssh_public_key": {"key_data": "/.ssh/id_rsa.pub"}}
            )

        # Valid ssh key
        args = self.format_arg(schema, {"ssh_public_key": {"key_data": valid_key}})
        self.assertEqual(args.ssh_public_key.key_data, valid_key)

        # Valid ssh key path
        # path = "/home/user/.ssh/id_rsa.pub"
        test_file = "test_id_rsa.pub"
        with open(test_file, "w") as f:
            f.write(valid_key)
        args = self.format_arg(schema, {"ssh_public_key": {"key_data": test_file}})
        self.assertEqual(args.ssh_public_key.key_data, valid_key)
        os.remove(test_file)
