# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from azure.cli.core.commands.parameters import (
    get_enum_type, get_location_completion_list, get_location_name_type
)
from .vendored_sdks.containerregistry.models import RegionalEndpoints


def load_arguments_preview(self, _):
    with self.argument_context("acr create") as c:
        c.argument(
            "regional_endpoints",
            arg_type=get_enum_type(RegionalEndpoints),
            is_preview=True,
            help="Indicates whether or not regional endpoints should be enabled for the registry. If not specified, this is set to disabled by default.",
        )

    with self.argument_context("acr update") as c:
        c.argument(
            "regional_endpoints",
            arg_type=get_enum_type(RegionalEndpoints),
            is_preview=True,
            help="Indicates whether or not regional endpoints should be enabled for the registry. If not specified, this is set to disabled by default.",
        )

    with self.argument_context("acr login") as c:
        c.argument(
            "endpoint",
            completer=get_location_completion_list,
            type=get_location_name_type(self.cli_ctx),
            is_preview=True,
            help="Log in to a specific regional endpoint of the container registry. Specify the region name "
                 "(e.g., eastus, westus2). Only applicable when regional endpoints are enabled."
        )
