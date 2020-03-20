# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import (
    tags_type,
    get_enum_type,
    resource_group_name_type,
    get_location_type
)
from azext_datashare.action import AddIdentity


def load_arguments(self, _):

    with self.argument_context('datashare account show') as c:
        c.argument('b1', help='The name of the share account a2.')
        c.argument('bc', help='c1')
