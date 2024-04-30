# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=protected-access
from azure.cli.core.aaz import AAZBoolArg
from azext_front_door.aaz.latest.network.front_door.waf_policy import Create as _WafPolicyCreate, \
    Update as _WafPolicyUpdate


class WafPolicyCreate(_WafPolicyCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.disabled = AAZBoolArg(
            options=['--disabled'],
            help='Create in a disabled state.',
            default=False,
            blank=True,
        )
        args_schema.enabled_state._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.location = 'global'
        if args.disabled.to_serialized_data():
            args.enabled_state = 'Disabled'
        else:
            args.enabled_state = 'Enabled'


class WafPolicyUpdate(_WafPolicyUpdate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.disabled = AAZBoolArg(
            options=['--disabled'],
            help='Create in a disabled state.',
            default=False,
            blank=True,
        )
        args_schema.enabled_state._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.location = 'global'
        if args.disabled.to_serialized_data():
            args.enabled_state = 'Disabled'
        else:
            args.enabled_state = 'Enabled'
