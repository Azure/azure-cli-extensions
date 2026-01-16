# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=unused-import

from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import get_enum_type


def load_arguments(self, _):
    with self.argument_context("nexusidentity gen-keys") as c:
        c.argument(
            "algorithm",
            arg_type=get_enum_type(
                [
                    "ed25519-sk",
                    "ecdsa-sk",
                ]
            ),
            help="Algorithm to use for generating keys. It can either be ecdsa-sk or ed25519-sk",
        )
