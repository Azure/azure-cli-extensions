# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: skip-file
# flake8: noqa

from azure.cli.core.aaz import *

@register_command(
    "workload-orchestration context set",
)
class SetContext(AAZCommand):
    """Set current context using context ID
    :example: Set a Context using ID
        az workload-orchestration context set --id /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.Edge/contexts/myContext
    """

    _aaz_info = {
        "version": "2025-08-01"
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

        _args_schema = cls._args_schema
        _args_schema.context_id = AAZStrArg(
            options=["--id"],
            help="The full resource ID of the Context.",
            required=True
        )
        return cls._args_schema

    def _execute_operations(self):
        self.pre_operations()
        # Extract context name and resource group from ID
        # ID format: /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Edge/contexts/{name}
        context_id = self.ctx.args.context_id.to_serialized_data()
        parts = context_id.split('/')
        if len(parts) != 9 or parts[6] != 'Microsoft.Edge' or parts[7] != 'contexts':
            raise CLIInternalError("Invalid context ID format")
        
        context_name = parts[8]
        resource_group = parts[4]
        
        self.post_operations()

    @register_callback
    def pre_operations(self):
        pass

    @register_callback
    def post_operations(self):
        pass

    def _output(self, *args, **kwargs):
        context_id = self.ctx.args.context_id.to_serialized_data()
        parts = context_id.split('/')
        context_name = parts[8]
        resource_group = parts[4]
        
        self.ctx.cli_ctx.config.set_value('workload_orchestration', 'context_id', context_id)
        self.ctx.cli_ctx.config.set_value('workload_orchestration', 'context_name', context_name)
        self.ctx.cli_ctx.config.set_value('workload_orchestration', 'resource_group', resource_group)
        
        return f"Successfully set current context using ID '{self.ctx.args.context_id}'"

class _SetContextHelper:
    """Helper class for SetContext"""

__all__ = ["SetContext"]
