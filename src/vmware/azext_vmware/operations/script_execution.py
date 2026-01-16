# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from ..aaz.latest.vmware.private_cloud.script_execution import GetExecutionLog
from azure.cli.core.aaz import register_command


@register_command(
    "vmware script-execution get-execution-log",
)
class ScriptExecutionGetExecutionLog(GetExecutionLog):
    """Return the logs for a script execution resource in a private cloud.

    :example: Return the logs for a script execution resource.
        az vmware script-execution get-execution-log --resource-group group1 --private-cloud-name cloud1 --script-execution-name addSsoServer --script-output-stream-type "[Information]"
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        return args_schema

    def pre_operations(self):
        super().pre_operations()
        args = self.ctx.args
        if not getattr(args, 'script_output_stream_type', None):
            args.script_output_stream_type = ["Information", "Warning", "Output", "Error"]
