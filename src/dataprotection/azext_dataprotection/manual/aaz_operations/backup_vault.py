# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=protected-access
# pylint: disable=line-too-long
# pylint: disable=consider-using-f-string

from azure.cli.core.aaz import (
    AAZStrArg, AAZBoolArg, AAZListArg, AAZResourceIdArg,
    AAZResourceIdArgFormat, AAZUndefined, has_value
)
from azure.cli.core.aaz.utils import assign_aaz_list_arg
from knack.log import get_logger
from azext_dataprotection.aaz.latest.dataprotection.backup_vault import Update as _Update
from azext_dataprotection.aaz.latest.dataprotection.backup_vault import Create as _Create
from ..helpers import critical_operation_map, transform_resource_guard_operation_request

logger = get_logger(__name__)


class Update(_Update):

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        if cls._args_schema is not None:
            return cls._args_schema
        cls._args_schema = super()._build_arguments_schema(*args, **kwargs)

        _args_schema = cls._args_schema
        _args_schema.tenant_id = AAZStrArg(
            options=["--tenant-id"],
            help="Tenant ID for cross-tenant calls"
        )
        return cls._args_schema

    def pre_operations(self):
        # Allow users to enter predefined shorthand instead of the full path, if necessary
        if has_value(self.ctx.args.resource_guard_operation_requests):
            self.ctx.args.resource_guard_operation_requests = assign_aaz_list_arg(
                self.ctx.args.resource_guard_operation_requests,
                self.ctx.args.resource_guard_operation_requests,
                element_transformer=lambda _, operation:
                    transform_resource_guard_operation_request(self, _, operation)
            )
        if has_value(self.ctx.args.tenant_id):
            # ValueError is raised when providing an incorrect tenant ID. Capturing it in a try block does not work.
            self.ctx.update_aux_tenants(str(self.ctx.args.tenant_id))

        if has_value(self.ctx.args.cmk_identity_type):
            cmk_identity_type = self.ctx.args.cmk_identity_type.to_serialized_data()
            if cmk_identity_type == "SystemAssigned":
                self.ctx.args.cmk_user_assigned_identity_id = None

        if has_value(self.ctx.args.type):
            identity_type = self.ctx.args.type.to_serialized_data()
            if identity_type == "SystemAssigned" or identity_type == "None":
                # In either scenario, passing user_assigned_identities (even an empty list) would cause a failure.
                self.ctx.args.user_assigned_identities = None


class Create(_Create):

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        if cls._args_schema is not None:
            return cls._args_schema
        cls._args_schema = super()._build_arguments_schema(*args, **kwargs)

        _args_schema = cls._args_schema
        _args_schema.mi_system_assigned = AAZBoolArg(
            options=["--mi-system-assigned"],
            help="Provide this flag to use system assigned identity",
            arg_group="Identity"
        )

        _args_schema.mi_user_assigned = AAZListArg(
            options=["--mi-user-assigned"],
            help="Space separated resource IDs to add user-assigned identities.",
            arg_group="Identity"
        )
        _args_schema.mi_user_assigned.Element = AAZResourceIdArg(
            fmt=AAZResourceIdArgFormat(template="/subscriptions/{subscription}/resourceGroups/{resource_group}"
                                                "/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{}")
        )

        return cls._args_schema

    def pre_operations(self):
        # Set the Managed Identity type and UAMI as per the command guidelines:
        #   https://github.com/Azure/azure-cli/blob/dev/doc/managed_identity_command_guideline.md
        # Includes deprecation of the old commands
        if has_value(self.ctx.args.type) or has_value(self.ctx.args.user_assigned_identities):
            logger.warning("TODO warning for old style, using --mi-system-assigned and --mi-user-assigned instead. "
                           "If either of the above is provided, any settings specified under these parameters will be "
                           "overridden.")
        
        if has_value(self.ctx.args.mi_system_assigned) or has_value(self.ctx.args.mi_user_assigned):
            mi_type = None
        
            if self.ctx.args.mi_system_assigned:
                mi_type = "SystemAssigned"
            
            if has_value(self.ctx.args.mi_user_assigned):
                # Set the user assigned value from
                user_assigned_identities = {}
                for identity in self.ctx.args.mi_user_assigned:
                    user_assigned_identities.update({
                        identity.to_serialized_data(): {}
                    })
                self.ctx.args.user_assigned_identities = user_assigned_identities

                # Updating the Managed Identity type
                mi_type = "UserAssigned" if mi_type is None else "SystemAssigned,UserAssigned"
            
            self.ctx.args.type = mi_type
