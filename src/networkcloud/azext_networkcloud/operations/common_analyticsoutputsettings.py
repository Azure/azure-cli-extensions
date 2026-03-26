# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=protected-access, too-few-public-methods
# pylint: disable=duplicate-code,no-member

"""
This is custom code for analytics output settings
"""

from azure.cli.core.aaz._base import has_value
from azure.cli.core.azclierror import (
    InvalidArgumentValueError,
    RequiredArgumentMissingError,
)
from knack.log import get_logger

logger = get_logger(__name__)


class AnalyticsOutputSettings:
    @classmethod
    def pre_operations_create(cls, args):
        cls.pre_operations_update(args)

    @classmethod
    def pre_operations_update(cls, args):
        if has_value(args.analytics_output_settings):
            if not has_value(args.analytics_output_settings.analytics_workspace_id):
                raise RequiredArgumentMissingError(
                    "Analytics workspace ID is missing for analytics output settings."
                )
            # if system assigned is provided, user assigned should not also be provided
            if args.analytics_output_settings.identity_type == "SystemAssignedIdentity":
                if has_value(args.analytics_output_settings.identity_resource_id):
                    logger.warning(
                        "For --analytics-output-settings, SystemAssignedIdentity type is "
                        "mutually exclusive with UserAssignedIdentity "
                        "type. Ignoring provided user-assigned identity %s",
                        args.analytics_output_settings.identity_resource_id,
                    )
                    args.analytics_output_settings.identity_resource_id = None
            elif args.analytics_output_settings.identity_type == "UserAssignedIdentity":
                if not has_value(args.analytics_output_settings.identity_resource_id):
                    raise InvalidArgumentValueError(
                        "User-assigned identity resource ID is missing for analytics output settings."
                    )
