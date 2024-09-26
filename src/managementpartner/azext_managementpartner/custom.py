# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

#  pylint: disable=protected-access


from azure.cli.core.aaz import has_value
from .aaz.latest.managementpartner import Show as _Show


class Show(_Show):

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        _args_schema = super()._build_arguments_schema(*args, **kwargs)
        _args_schema.partner_id._required = False
        return _args_schema

    def pre_operations(self):
        args = self.ctx.args
        if not has_value(args.partner_id):
            args.partner_id = ''
