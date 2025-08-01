from datetime import datetime

from mcp.types import ToolAnnotations
from mcp.server.fastmcp import FastMCP, Context
from mcp.server.fastmcp.tools import Tool
from mcp.server.fastmcp.resources import FunctionResource
from mcp.server.streamable_http import EventStore
from azure.cli.core import AzCli
from knack import log
from pydantic import BaseModel, Field
from typing_extensions import Annotated

from .command_introspection import (
    build_command_help_info,
    build_command_group_help_info,
    handle_arg_schema,
    handle_help_schema,
)

logger = log.get_logger(__name__)


class MCPConfirmation(BaseModel):
    confirmation: Annotated[str, Field(
        description="Whether to confirm the command execution. "
                    "If Y/y/YES/yes, the command will be executed without confirmation.",
        default="false"
    )]


class AzCLIBridge:
    """Bridge layer between AzCLI and AzMCP that provides command introspection and execution."""

    def __init__(self, cli_ctx: AzCli):
        self.cli_ctx = cli_ctx
        self._ensure_commands_loaded()
        self.command_table = self.cli_ctx.invocation.commands_loader.command_table
        self.group_table = self.cli_ctx.invocation.commands_loader.command_group_table

    def _ensure_commands_loaded(self):
        """Ensure CLI commands are loaded."""
        start_at = datetime.now()
        self.cli_ctx.invocation.commands_loader.load_command_table(None)
        try:
            self.cli_ctx.invocation.commands_loader.load_arguments()
        except ImportError:
            logger.warning("Failed to load command arguments")
        logger.debug("Commands loaded in %s seconds", (datetime.now() - start_at).total_seconds())

    def get_command_help(self, command_name: str):
        """Get help content for a specific command."""
        # Check if it's a command
        command = self.command_table.get(command_name)
        if command:
            return build_command_help_info(command_name, command)
        
        # Check if it's a command group
        command_group = self.group_table.get(command_name)
        if command_group is not None:
            return build_command_group_help_info(command_name, command_group, self.command_table, self.group_table)

        return 'Command or group not found'

    def get_command_arguments_schema(self, command_name: str):
        """Get argument help and schema for a specific command."""
        # Implementation here
        command = self.command_table.get(command_name)
        if not command:
            return None
        if hasattr(command, '_args_schema'):
            return handle_arg_schema(command._args_schema)
        help_info = build_command_help_info(command_name, command)
        if help_info and 'arguments' in help_info:
            return handle_help_schema(help_info)
        return None

    def get_default_arguments(self, command_name: str):
        """Get default arguments for a specific command."""
        schema = self.get_command_arguments_schema(command_name)
        if not schema:
            return None
        default_args = {}
        for arg_name, arg_info in schema.items():
            if 'default' in arg_info and arg_info['default'] is not None:
                default_args[arg_name] = arg_info['default']
        return default_args

    def invoke_command(self, command_name: str, arguments: dict | None = None):
        """Invoke a command with JSON-described arguments."""
        from azure.cli.core.commands import LongRunningOperation, _is_poller, _is_paged, AzCliCommandInvoker

        command = self.command_table.get(command_name)
        if not command:
            return None
        if arguments is None:
            arguments = {}
        default_args = self.get_default_arguments(command_name)
        if default_args:
            arguments = {**default_args, **arguments}
        arguments = {"cmd": command, **arguments}  # Ensure 'cmd' is passed to the command
        result = command(arguments)
        transform_op = command.command_kwargs.get('transform', None)
        if transform_op:
            result = transform_op(result)

        if _is_poller(result):
            result = LongRunningOperation(command.cli_ctx, 'Starting {}'.format(command.name))(result)
        elif _is_paged(result):
            result = list(result)

        from azure.cli.core.util import todict
        result = todict(result, AzCliCommandInvoker.remove_additional_prop_layer)
        return {'result': result}


class AzMCP(FastMCP):

    def __init__(
            self,
            cli_ctx: AzCli,
            name: str | None = None,
            instructions: str | None = None,
            event_store: EventStore | None = None,
            *,
            tools: list[Tool] | None = None):
        super().__init__(
            name or "AZ MCP",
            instructions,
            event_store,
            tools=tools)
        self.cli_ctx = cli_ctx
        self.az_cli_bridge = AzCLIBridge(self.cli_ctx)
        self._register_primitives()
        # self._register_resources()
    
    def _register_primitives(self):
        super().resource(
            "az://{command_name_path}",
            name="Azure CLI Command Help",
            description="Retrieve comprehensive help documentation for Azure CLI commands and command groups. "
                   "Provides detailed information including command syntax, parameters, examples, and usage patterns. "
                   "Path format: 'az://command/subcommand' (e.g., 'az://login', 'az://vm/create', 'az://storage/account/list')",
            mime_type="application/json",
        )(self.command_help_resource)
        super().tool(
            "get_az_cli_command_schema",
            title="Get Azure CLI Command Schema",
            description="Retrieve the detailed argument schema and parameter specifications for any Azure CLI command. "
                "Provides comprehensive information about required parameters, optional flags, data types, "
                "validation rules, and parameter descriptions. Input should be the command name without the 'az' "
                "prefix (e.g., 'vm create', 'storage account list', 'network vnet show').",
            annotations=ToolAnnotations(
                title="Get Azure CLI Command Schema",
                readOnlyHint=True,
            ),
            structured_output=True,
        )(self.get_command_schema)
        super().tool(
            "invoke_az_cli_command",
            title="Invoke Azure CLI Command",
            description="Execute an Azure CLI command with specified arguments in JSON format. "
                "This tool allows you to run any Azure CLI command programmatically, passing arguments as a JSON object."
                "The key in arguments should match the command's argument names, instead of the options. "
                "This tool must be called after the command schema tool to ensure the command is valid.",
            annotations=ToolAnnotations(
                title="Invoke Azure CLI Command",
                destructiveHint=True,
            ),
            structured_output=True,
        )(self.invoke_command)

    def _register_resources(self):
        for group_name in self.az_cli_bridge.group_table.keys():
            async def resource_fn(captured_name=group_name) -> str:
                return self.az_cli_bridge.get_command_help(captured_name)

            self.add_resource(FunctionResource.from_function(
                fn=resource_fn,
                uri=f'az://{"/".join(group_name.split())}',
                name=f'Azure CLI Group Help for `az {group_name}`',
                description=f'Retrieve help documentation for the Azure CLI group `az {group_name}`.',
                mime_type="application/json",
            ))
        for command_name in self.az_cli_bridge.command_table.keys():
            async def resource_fn(captured_name=command_name) -> str:
                return self.az_cli_bridge.get_command_help(captured_name)

            self.add_resource(FunctionResource.from_function(
                fn=resource_fn,
                uri=f'az://{"/".join(command_name.split())}',
                name=f'Azure CLI Command Help for `az {command_name}`',
                description=f'Retrieve help documentation for the Azure CLI command `az {command_name}`.',
                mime_type="application/json",
            ))

    def command_help_resource(self, command_name_path: str) -> str:
        return self.az_cli_bridge.get_command_help(command_name_path.split('/'))
    
    def get_command_schema(self, command_name: str) -> dict | None:
        """Get the argument schema for a specific command."""
        if command_name.startswith('az '):
            command_name = command_name[3:]  # Remove 'az ' prefix if present
        return self.az_cli_bridge.get_command_arguments_schema(command_name)

    async def invoke_command(self, command_name: str, arguments: dict, ctx: Context) -> dict | None:
        """Invoke a command with JSON-described arguments."""
        if command_name.startswith('az '):
            command_name = command_name[3:]
        verb = command_name.split()[-1]
        if verb not in ['list', 'show']:
            result = await ctx.elicit("This is a destructive command. Do you want to continue? (y/N)", MCPConfirmation)
            if not (result.action == "accept" and result.data.confirmation.lower() in ["y", "yes"]):
                return None
        return self.az_cli_bridge.invoke_command(command_name, arguments)
