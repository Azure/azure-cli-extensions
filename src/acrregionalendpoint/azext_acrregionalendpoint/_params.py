# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from azure.cli.core.commands.parameters import get_three_state_flag


def load_arguments_preview(self, _):
    with self.argument_context("acr create") as c:
        c.argument(
            "enable_regional_endpoints",
            arg_type=get_three_state_flag(),
            is_preview=True,
            help="Enable or disable regional endpoints for the registry.",
        )

    with self.argument_context("acr update") as c:
        c.argument(
            "enable_regional_endpoints",
            arg_type=get_three_state_flag(),
            is_preview=True,
            help="Enable or disable regional endpoints for the registry.",
        )

    with self.argument_context("acr login") as c:
        c.argument(
            "all_endpoints",
            action='store_true',
            is_preview=True,
            help="Enable login to all regional endpoints of the container registry."
        )
