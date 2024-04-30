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
from azext_dataprotection.aaz.latest.dataprotection.resource_guard import Update as _Update
from azext_dataprotection.aaz.latest.dataprotection.resource_guard import Unlock as _Unlock
from azext_dataprotection.manual.enums import get_resource_type_values
from ..helpers import critical_operation_map, transform_resource_guard_operation_request

logger = get_logger(__name__)


class Update(_Update):

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        if cls._args_schema is not None:
            return cls._args_schema
        cls._args_schema = super()._build_arguments_schema(*args, **kwargs)

        _args_schema = cls._args_schema
        _args_schema.resource_type = AAZStrArg(
            options=["--resource-type"],
            help="Type of the resource associated with the protected operations.",
            enum=get_resource_type_values()
        )
        return cls._args_schema

    def pre_operations(self):
        if has_value(self.ctx.args.critical_operation_exclusion_list):
            resource_type = self.ctx.args.resource_type.to_serialized_data()
            if resource_type:
                self.ctx.args.critical_operation_exclusion_list = assign_aaz_list_arg(
                    self.ctx.args.critical_operation_exclusion_list,
                    self.ctx.args.critical_operation_exclusion_list,
                    element_transformer=lambda _, e:
                        resource_type + critical_operation_map.get(str(e), str(e))
                        if str(e) in critical_operation_map else e
                )
            else:
                # Issue a warning if --resource-type not given but --critical-operation-exclusion-list is given.
                # List can be empty as well.
                logger.warning("WARNING: --resource-type argument is required to update "
                               "--critical-operation-exclusion-list.")
                self.ctx.args.critical_operation_exclusion_list = AAZUndefined


class Unlock(_Unlock):

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
