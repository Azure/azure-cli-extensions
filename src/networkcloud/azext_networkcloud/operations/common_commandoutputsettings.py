# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=protected-access, too-few-public-methods
# pylint: disable=duplicate-code,no-member

"""
This is custom code for command output settings
"""

from azure.cli.core.aaz._base import has_value
from azure.cli.core.azclierror import InvalidArgumentValueError
from knack.log import get_logger

logger = get_logger(__name__)


class CommandOutputSettings:
    @classmethod
    def pre_operations_create(cls, args):
        # unsure yet if anything between create and update needs to
        # be different

        cls.pre_operations_update(args)

    @classmethod
    def pre_operations_update(cls, args):
        if args.command_output_settings:
            # if system assigned is provided, user assigned should not also be provided
            if args.command_output_settings.identity_type == "SystemAssignedIdentity":
                if has_value(args.command_output_settings.identity_resource_id):
                    logger.warning(
                        "SystemAssignedIdentity type is mutually exclusive with UserAssignedIdentity type. Ignoring "
                        "provided user-assigned identity %s",
                        args.command_output_settings.identity_resource_id,
                    )
                    args.command_output_settings.identity_resource_id = None

            if args.command_output_settings.identity_type == "UserAssignedIdentity":
                if not has_value(args.command_output_settings.identity_resource_id):
                    raise InvalidArgumentValueError(
                        "User-assigned identity resource ID is missing for command output settings."
                    )
