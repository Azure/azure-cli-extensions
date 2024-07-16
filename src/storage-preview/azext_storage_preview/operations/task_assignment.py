# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger
from datetime import datetime
from azure.cli.core.aaz import has_value
from azure.cli.core.aaz.exceptions import AAZUnknownFieldError
from ..aaz.latest.storage.account.task_assignment import Create as _TaskAssignmentCreate
from ..aaz.latest.storage.account.task_assignment import Update as _TaskAssignmentUpdate

logger = get_logger(__name__)

datatime_format = "%Y-%m-%dT%H:%M:%S.%fZ"


class TaskAssignmentCreate(_TaskAssignmentCreate):
    def pre_operations(self):
        args = self.ctx.args
        try:
            if has_value(args.execution_context.trigger.parameters.start_on):
                start_on = args.execution_context.trigger.parameters.start_on
                formatted_time = datetime.strptime(str(start_on), datatime_format)
                args.execution_context.trigger.parameters.start_on = \
                    formatted_time.strftime(datatime_format)[:-1] + "0Z"
            if has_value(args.execution_context.trigger.parameters.start_from):
                start_from = args.execution_context.trigger.parameters.start_from
                formatted_time = datetime.strptime(str(start_from), datatime_format)
                args.execution_context.trigger.parameters.start_from = \
                    formatted_time.strftime(datatime_format)[:-1] + "0Z"
            if has_value(args.execution_context.trigger.parameters.end_by):
                end_by = args.execution_context.trigger.parameters.end_by
                formatted_time = datetime.strptime(str(end_by), datatime_format)
                args.execution_context.trigger.parameters.end_by = \
                    formatted_time.strftime(datatime_format)[:-1] + "0Z"
        except AAZUnknownFieldError:
            pass


class TaskAssignmentUpdate(_TaskAssignmentUpdate):
    def pre_operations(self):
        args = self.ctx.args
        try:
            if has_value(args.execution_context.trigger.parameters.start_on):
                start_on = args.execution_context.trigger.parameters.start_on
                formatted_time = datetime.strptime(str(start_on), datatime_format)
                args.execution_context.trigger.parameters.start_on = \
                    formatted_time.strftime(datatime_format)[:-1] + "0Z"
            if has_value(args.execution_context.trigger.parameters.start_from):
                start_from = args.execution_context.trigger.parameters.start_from
                formatted_time = datetime.strptime(str(start_from), datatime_format)
                args.execution_context.trigger.parameters.start_from = \
                    formatted_time.strftime(datatime_format)[:-1] + "0Z"
            if has_value(args.execution_context.trigger.parameters.end_by):
                end_by = args.execution_context.trigger.parameters.end_by
                formatted_time = datetime.strptime(str(end_by), datatime_format)
                args.execution_context.trigger.parameters.end_by = \
                    formatted_time.strftime(datatime_format)[:-1] + "0Z"
        except AAZUnknownFieldError:
            pass
