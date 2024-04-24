# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from ..aaz.latest.vmware.private_cloud import Create as _PrivateCloudCreate, Update as _PrivateCloudUpdate

from knack.arguments import CLICommandArgument


class PrivateCloudCreate(_PrivateCloudCreate):

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZBoolArg
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.mi_system_assigned = AAZBoolArg(
            options=["--mi-system-assigned"],
            help="Enable a system assigned identity."
        )
        # use mi_system_assigned to assign this value in pre_operations
        args_schema.identity._registered = False
        return args_schema

    def load_arguments(self):
        super().load_arguments()
        # This is a special customization which to overwrite default yes argument in framework
        # to backword compatible with the old command.
        if self.confirmation:
            self.arguments['yes'] = CLICommandArgument(
                dest='yes', options_list=['--yes', '-y', '--accept-eula'], action='store_true',
                help='Accept the end-user license agreement without prompting.')

    def pre_operations(self):
        args = self.ctx.args
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
