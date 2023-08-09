# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from ..aaz.latest.vmware.private_cloud import Create as _PrivateCloudCreate, Update as _PrivateCloudUpdate

from ..custom import LEGAL_TERMS
from knack.prompting import prompt_y_n
from knack.util import CLIError


class PrivateCloudCreate(_PrivateCloudCreate):

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZBoolArg
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.accept_eula = AAZBoolArg(
            options=["--accept-eula"],
            help="Accept the end-user license agreement without prompting."
        )
        args_schema.yes = AAZBoolArg(
            options=["--yes", "-y"],
            help="Do not prompt for confirmation"
        )
        args_schema.mi_system_assigned = AAZBoolArg(
            options=["--mi-system-assigned"],
            help="Enable a system assigned identity."
        )
        # use mi_system_assigned to assign this value
        args_schema.identity._registered = False
        return args_schema

    def pre_operations(self):
        args = self.args
        if not args.accept_eula:
            print(LEGAL_TERMS)
            msg = 'Do you agree to the above additional terms for AVS?'
            if not args.yes and not prompt_y_n(msg, default="n"):
                raise CLIError('Operation cancelled.')
        if args.mi_system_assigned:
            args.identity.type = "SystemAssigned"
        else:
            args.identity.type = "None"


class PrivateCloudUpdate(_PrivateCloudUpdate):

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.identity._registered = False
        # updated by vmware private-cloud enable-cmk-encryption/disable-cmk-encryption
        args_schema.encryption._registered = False
        # updated by vmware private-cloud add-identity-source/delete-identity-source
        args_schema.identity_sources._registered = False
        return args_schema
