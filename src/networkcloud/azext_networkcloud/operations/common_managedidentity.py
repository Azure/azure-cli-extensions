# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=protected-access, too-few-public-methods
# pylint: disable=duplicate-code,no-member

"""
This custom code for managed identity
"""
from azure.cli.core.aaz import (
    AAZBoolArg,
    AAZListArg,
    AAZResourceIdArg,
    AAZResourceIdArgFormat,
)
from azure.cli.core.aaz._base import has_value


class ManagedIdentity:
    @staticmethod
    def build_arguments_schema(args_schema):
        args_schema.mi_system_assigned = AAZBoolArg(
            options=["--mi-system-assigned"],
            arg_group="Managed Identity",
            help="Enable system assigned identity",
        )
        args_schema.mi_user_assigned = AAZListArg(
            options=["--mi-user-assigned"],
            arg_group="Managed Identity",
            help="Space separated resource IDs to add user-assigned identities.",
        )
        args_schema.mi_user_assigned.Element = AAZResourceIdArg(
            fmt=AAZResourceIdArgFormat(
                template="/subscriptions/{subscription}/resourceGroups/{resource_group}"
                "/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{}"
            )
        )
        args_schema.identity._registered = False
        return args_schema

    @classmethod
    def pre_operations_create(cls, args):
        # set identity.type to None if args.mi_system_assigned and args.mi_user_assigned are not set
        # but only for create operations. For update operations, we should allow the default to remain unchanged.
        if not has_value(args.mi_system_assigned) and not has_value(
            args.mi_user_assigned
        ):
            args.identity.type = "None"

        cls.pre_operations_update(args)

    @classmethod
    def pre_operations_update(cls, args):
        # set identity.type to "SystemAssigned" if args.mi_system_assigned is set
        if args.mi_system_assigned:
            args.identity.type = "SystemAssigned"

        # set identity.type to "UserAssigned" if args.mi_user_assigned is set
        if has_value(args.mi_user_assigned) and len(args.mi_user_assigned) > 0:
            args.identity.type = "UserAssigned"
            user_assigned_identities = {}
            for identity in args.mi_user_assigned:
                user_assigned_identities.update({identity.to_serialized_data(): {}})
            args.identity.user_assigned_identities = user_assigned_identities

        # if both mi_system_assigned and mi_user_assigned are set,
        # then set identity.type to "SystemAssigned,UserAssigned"
        if args.mi_system_assigned and (
            has_value(args.mi_user_assigned) and len(args.mi_user_assigned) > 0
        ):
            args.identity.type = "SystemAssigned,UserAssigned"
