# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------

from azure.cli.core.aaz import has_value
from azure.cli.core.azclierror import (
    InvalidArgumentValueError
)

from msrestazure.tools import is_valid_resource_id

from ..aaz.latest.load._create import Create


class LoadTestCreate(Create):

    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()

        # encryption_identity_type args are not exposed
        # encryption_identity_type is populated based on encryption_identity arg value
        args = [(name, arg) for (name, arg) in args if name not in ["encryption_identity_type"]]
        return args

    def pre_operations(self):
        args = self.ctx.args
        identity_type_str = args.identity_type.to_serialized_data()

        if has_value(args.encryption_identity):
            encryption_identity_id = args.encryption_identity.to_serialized_data()
            if is_valid_resource_id(encryption_identity_id):
                args.encryption_identity_type = "UserAssigned"
                if identity_type_str.lower() == "none":
                    args.identity_type = "UserAssigned"
                elif identity_type_str.lower() == "systemassigned":
                    args.identity_type = "SystemAssigned,UserAssigned"
                args.user_assigned[encryption_identity_id] = {}
            else:
                raise InvalidArgumentValueError("--encryption-identity is not a valid Azure resource ID.")
