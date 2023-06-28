# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.aaz import AAZStrArg
from azext_dataprotection.aaz.latest.dataprotection.recovery_point import List as _RecoveryPointList
from ..helpers import validate_recovery_point_datetime_format


class RecoveryPointList(_RecoveryPointList):

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        if cls._args_schema is not None:
            return cls._args_schema
        cls._args_schema = super()._build_arguments_schema(*args, **kwargs)
        _args_schema = cls._args_schema
        _args_schema.start_time = AAZStrArg(
            options=["--start-time"],
            help="Specify the start date time in UTC (yyyy-mm-ddTHH:MM:SS)",
        )
        _args_schema.end_time = AAZStrArg(
            options=["--end-time"],
            help="Specify the end date time in UTC (yyyy-mm-ddTHH:MM:SS)",
        )
        _args_schema.filter._registered = False
        _args_schema.skip_token._registered = False
        return cls._args_schema

    def pre_operations(self):
        start_time = validate_recovery_point_datetime_format(self.ctx.args.start_time)
        end_time = validate_recovery_point_datetime_format(self.ctx.args.end_time)
        rp_filter = ""
        if start_time:
            rp_filter += "startDate eq '" + start_time + "'"
        if end_time:
            if self.ctx.args.start_time:
                rp_filter += " and "
            rp_filter += "endDate eq '" + end_time + "'"
        self.ctx.args.filter = rp_filter
