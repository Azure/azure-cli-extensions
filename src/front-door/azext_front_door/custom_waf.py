# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.aaz import AAZBoolArg
from azext_front_door.aaz.latest.network.front_door.waf_policy import Create as _WafPolicyCreate, \
    Update as _WafPolicyUpdate


class WafPolicyCreate(_WafPolicyCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.identity_type = AAZBoolArg(
            options=['--disabled'],
            help='Create in a disabled state.',
            default=False,
            blank=False
        )
        args_schema.enabled_state._registered = False
        return args_schema

    def pre_operation(self):
        args = self.ctx.args
        args.location = 'global'
        args.enabled_state = not args.disabled


class WafPolicyUpdate(_WafPolicyUpdate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.identity_type = AAZBoolArg(
            options=['--disabled'],
            help='Create in a disabled state.',
            default=False,
            blank=False
        )
        args_schema.enabled_state._registered = False
        return args_schema

    def pre_operation(self):
        args = self.ctx.args
        args.location = 'global'
        args.enabled_state = not args.disabled
