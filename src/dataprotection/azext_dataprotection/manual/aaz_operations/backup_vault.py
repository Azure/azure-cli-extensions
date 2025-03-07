# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=protected-access
# pylint: disable=line-too-long
# pylint: disable=consider-using-f-string

from azure.cli.core.aaz import AAZStrArg, AAZUndefined, has_value
from azure.cli.core.aaz.utils import assign_aaz_list_arg
from knack.log import get_logger
from azext_dataprotection.aaz.latest.dataprotection.backup_vault import Update as _Update
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
