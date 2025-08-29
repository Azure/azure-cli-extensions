# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: skip-file
# flake8: noqa

from azure.cli.core.aaz import *

@register_command(
    "workload-orchestration context current",
)
class CurrentContext(AAZCommand):
    """Show current context information
    :example: Show current context
        az workload-orchestration context current
    """

    _aaz_info = {
        "version": "2025-06-01"
    }

    def _handler(self, command_args):
        super()._handler(command_args)
        self._execute_operations()
        return self._output()

    _args_schema = None

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        if cls._args_schema is not None:
            return cls._args_schema
        cls._args_schema = super()._build_arguments_schema(*args, **kwargs)
        return cls._args_schema

    def _execute_operations(self):
        self.pre_operations()
        # No operations needed - just reading config
        self.post_operations()

    @register_callback
    def pre_operations(self):
        pass

    @register_callback
    def post_operations(self):
        pass

    def _output(self, *args, **kwargs):
        context_id = self.ctx.cli_ctx.config.get('workload_orchestration', 'context_id', None)
        context_name = self.ctx.cli_ctx.config.get('workload_orchestration', 'context_name', None)
        resource_group = self.ctx.cli_ctx.config.get('workload_orchestration', 'resource_group', None)

        if not context_id or not context_name or not resource_group:
            return "No current context is set"

        return {
            "contextId": context_id,
            "name": context_name,
            "resourceGroup": resource_group
        }

class _CurrentContextHelper:
    """Helper class for CurrentContext"""

__all__ = ["CurrentContext"]
