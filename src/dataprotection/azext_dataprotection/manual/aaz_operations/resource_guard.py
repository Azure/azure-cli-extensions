# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=protected-access
# pylint: disable=line-too-long
from azure.cli.core.aaz import AAZStrArg, AAZUndefined
from azext_dataprotection.aaz.latest.dataprotection.resource_guard import Update as _Update
from azext_dataprotection.manual.enums import get_resource_type_values
from knack.log import get_logger
from ..helpers import critical_operation_map

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
        critical_operation_exclusion_list = self.ctx.args.critical_operation_exclusion_list
        resource_type = self.ctx.args.resource_type
        if resource_type and critical_operation_exclusion_list.to_serialized_data() != AAZUndefined:
            for idx, critical_operation in enumerate(critical_operation_exclusion_list):
                critical_operation_id = critical_operation_map.get(str(critical_operation), str(critical_operation))
                critical_operation_exclusion_list[idx] = str(resource_type) + critical_operation_id
        else:
            if critical_operation_exclusion_list.to_serialized_data() != AAZUndefined:
                logger.warning("WARNING: --resource-type argument is required to update --critical-operation-exclusion-list.")
                self.ctx.args.critical_operation_exclusion_list = AAZUndefined
