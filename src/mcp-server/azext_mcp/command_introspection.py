import ast
from importlib import import_module
import inspect
from pathlib import Path
import re
import textwrap

from azure.cli.core.aaz import AAZArgumentsSchema, AAZObjectType, AAZDictType, AAZListType, AAZIntType, AAZStrType, AAZBoolType, AAZFloatType, AAZAnyType, AAZIntArg, AAZStrArg, AAZBoolArg, AAZFloatArg, AAZBaseArg
from azure.cli.core.aaz._base import AAZBaseType, _AAZUndefinedType
from knack import log
import yaml

logger = log.get_logger(__name__)

# Constants moved from AzCLIBridge class
STORED_DEPRECATION_KEY = ["expiration", "target", "redirect", "hide"]
IMPORT_AAZ_EXPRESS = re.compile(r'^\s*from (.*\.)?aaz(\..*)? .*$')
COMMAND_ARGS_EXPRESS = re.compile(r'^.*[\s\(]command_args=.*$')


def get_command_help_info(name: str, command=None):
    """Get help information for a command.
    
    Args:
        name: Command name
        command: Command object (optional)
        
    Returns:
        dict: Help information with at least 'short-summary' key
    """
    if command and hasattr(command, 'AZ_HELP') and command.AZ_HELP:
        return command.AZ_HELP
    elif command and hasattr(command, 'help') and command.help:
        return command.help
    from knack.help_files import helps
    if name in helps:
        return yaml.safe_load(helps[name])
    else:
        return {"short-summary": "No help available for this command"}


def get_command_codegen_info(command):
    """Get code generation information for a command.
    
    Args:
        command: Command object to analyze
        
    Returns:
        dict or None: Code generation info with 'version' and 'type' keys, or None
    """
    from azure.cli.core.commands import AzCliCommand
    from azure.cli.core.aaz import AAZCommand
    if isinstance(command, AAZCommand):
        return {
            "version": "v2",
            "type": "Atomic"
        }

    if isinstance(command, AzCliCommand):
        if 'command_operation' not in command.command_kwargs:
            return None

        command_operation = command.command_kwargs['command_operation']
        is_v2_convenience = False
        is_generated = False
        if getattr(command_operation, 'op_path', None):
            operation_path = command_operation.op_path
            operation_module_path = operation_path.split("#")[0]
            op = command_operation.get_op_handler(operation_path)
            func_map = get_module_functions(operation_module_path)
            op_source = expand_all_functions(op, func_map)
            for line in op_source.splitlines():
                if IMPORT_AAZ_EXPRESS.match(line):
                    is_v2_convenience = True
                    break
                if COMMAND_ARGS_EXPRESS.match(line):
                    is_v2_convenience = True

            path_parts = list(Path(inspect.getfile(op)).parts)
            if "generated" in path_parts:
                is_generated = True

        if not is_v2_convenience and getattr(command_operation, 'getter_op_path', None):
            op = command_operation.get_op_handler(command_operation.getter_op_path)
            op_source = inspect.getsource(op)
            for line in op_source.splitlines():
                if IMPORT_AAZ_EXPRESS.match(line):
                    is_v2_convenience = True
                    break
                if COMMAND_ARGS_EXPRESS.match(line):
                    is_v2_convenience = True

            path_parts = list(Path(inspect.getfile(op)).parts)
            if "generated" in path_parts:
                is_generated = True

        if not is_v2_convenience and getattr(command_operation, 'setter_op_path', None):
            op = command_operation.get_op_handler(command_operation.setter_op_path)
            op_source = inspect.getsource(op)
            for line in op_source.splitlines():
                if IMPORT_AAZ_EXPRESS.match(line):
                    is_v2_convenience = True
                    break
                if COMMAND_ARGS_EXPRESS.match(line):
                    is_v2_convenience = True

            path_parts = list(Path(inspect.getfile(op)).parts)
            if "generated" in path_parts:
                is_generated = True

        if not is_v2_convenience and getattr(command_operation, 'custom_function_op_path', None):
            op = command_operation.get_op_handler(command_operation.custom_function_op_path)
            op_source = inspect.getsource(op)
            for line in op_source.splitlines():
                if IMPORT_AAZ_EXPRESS.match(line):
                    is_v2_convenience = True
                    break
                if COMMAND_ARGS_EXPRESS.match(line):
                    is_v2_convenience = True

            path_parts = list(Path(inspect.getfile(op)).parts)
            if "generated" in path_parts:
                is_generated = True
        if is_v2_convenience:
            return {
                "version": "v2",
                "type": "Convenience"
            }
        elif is_generated:
            return {
                "version": "v1",
                "type": "SDK"
            }
    return None


def extract_argument_deprecation_info(argument_settings):
    """Extract deprecation information from argument settings.
    
    Returns:
        dict or None: Deprecation info if present, None otherwise
    """
    if argument_settings.get("deprecate_info", None) is None:
        return None
    
    deprecate_info = {}
    for info_key in STORED_DEPRECATION_KEY:
        if hasattr(argument_settings["deprecate_info"], info_key) and \
                getattr(argument_settings["deprecate_info"], info_key):
            deprecate_info[info_key] = getattr(argument_settings["deprecate_info"], info_key)
    
    return deprecate_info if deprecate_info else None


def extract_argument_options(argument_settings):
    """Extract options list from argument settings.
    
    Returns:
        list: Sorted list of argument options
    """
    if not argument_settings.get("options_list", None):
        return []
    
    raw_options_list = argument_settings["options_list"]
    option_list = set()
    for opt in raw_options_list:
        opt_type = opt.__class__.__name__
        if opt_type == "str":
            option_list.add(opt)
        elif opt_type == "Deprecated":
            if hasattr(opt, "hide") and opt.hide:
                continue
            if hasattr(opt, "target"):
                option_list.add(opt.target)
        else:
            logger.warning("Unsupported option type: %s", opt_type)
    
    return sorted(option_list)


def extract_argument_options_deprecation(argument_settings):
    """Extract deprecation information for argument options.
    
    Returns:
        list: List of option deprecation info dictionaries
    """
    if not argument_settings.get("options_list", None):
        return []
    
    raw_options_list = argument_settings["options_list"]
    option_deprecation_list = []
    for opt in raw_options_list:
        opt_type = opt.__class__.__name__
        if opt_type != "Deprecated":
            continue
        opt_deprecation = {}
        for info_key in STORED_DEPRECATION_KEY:
            if hasattr(opt, info_key) and getattr(opt, info_key):
                opt_deprecation[info_key] = getattr(opt, info_key)
        if opt_deprecation:
            option_deprecation_list.append(opt_deprecation)
    
    return option_deprecation_list


def extract_argument_type(argument):
    """Extract type information from argument settings.
    
    Returns:
        str or None: Type name if present, None otherwise
    """
    argument_settings = argument.type.settings
    if not argument_settings.get("type", None):
        return None

    configured_type = argument_settings["type"]
    raw_type = None
    if hasattr(configured_type, "__name__"):
        raw_type = configured_type.__name__
    elif hasattr(configured_type, "__class__"):
        raw_type = configured_type.__class__.__name__
    else:
        logger.warning("Unsupported type: %s", configured_type)
        return None
    
    return raw_type if raw_type in ["str", "int", "float", "bool", "file_type"] else "custom_type"


def get_module_functions(path):
    """Get all functions from a module by import path.
    
    Args:
        path: Module import path (e.g., 'azure.cli.command.module')
        
    Returns:
        dict or None: Dictionary mapping function names to function objects, or None
    """
    try:
        module = import_module(path)
        functions = inspect.getmembers(module, predicate=inspect.isfunction)
        return dict(functions)

    except ModuleNotFoundError:
        return None  # bypass functions in sdk


def expand_all_functions(func, func_map):
    """Expand function source code by including all called functions.
    
    Args:
        func: The function to expand
        func_map: Dictionary mapping function names to function objects
        
    Returns:
        str: Expanded source code
    """
    source = ""
    try:
        source = textwrap.dedent(inspect.getsource(func))
    except (OSError, TypeError) as e:
        # https://docs.python.org/3/library/inspect.html#inspect.getsource
        logger.warning("Cannot retrieve the source code of %s: %s", func, e)

    if func_map is None:
        return source

    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            function_name = node.func.id
            function = func_map.get(function_name, None)
            # skip recursion and `locals()`
            if function_name == func.__name__ or function is None:
                continue

            source += expand_all_functions(function, func_map)

    return source


def build_argument_info(argument):
    """Build complete argument information from argument settings.
    
    Args:
        argument: Raw argument object with type and settings
        
    Returns:
        dict: Complete argument information dictionary
    """
    argument_settings = argument.type.settings
    arg_info = {}
    
    # Extract options
    options = extract_argument_options(argument_settings)
    if options:
        arg_info["options"] = options
    
    # Extract type
    arg_type = extract_argument_type(argument)
    if arg_type:
        arg_info["type"] = arg_type
    
    # Extract deprecation info
    deprecation_info = extract_argument_deprecation_info(argument_settings)
    if deprecation_info:
        arg_info["deprecate_info"] = deprecation_info
    
    # Extract options deprecation
    options_deprecation = extract_argument_options_deprecation(argument_settings)
    if options_deprecation:
        arg_info["options_deprecate_info"] = options_deprecation
    
    return arg_info


def build_command_help_info(name: str, command=None):
    """Build comprehensive help information for a command.
    
    Args:
        name: Command name
        command: Command object (optional)
        command_table: Command table for resolving subcommands (optional)
        
    Returns:
        dict: Complete command help information including arguments
    """
    if command is None:
        return {"short-summary": "Command not found"}
    
    help_info = get_command_help_info(name, command)
    help_info['arguments'] = {}
    
    # Add code generation info
    codegen_info = get_command_codegen_info(command)
    if codegen_info:
        help_info['codegen_info'] = codegen_info
    
    # # Add arguments schema if available
    # if hasattr(command, '_args_schema'):
    #     help_info['arguments_schema'] = command._args_schema
    
    # Process command arguments
    for arg_name, argument in command.arguments.items():
        if argument.type is None:
            continue
        settings = argument.type.settings
        # Skip ignore actions
        if settings.get("action", None):
            action = settings["action"]
            if hasattr(action, "__name__") and action.__name__ == "IgnoreAction":
                continue

        # Build argument info using new extract functions
        arg_info = build_argument_info(argument)
        arg_info["name"] = settings["dest"]

        # Add additional argument properties
        if settings.get("required", False):
            arg_info["required"] = True
        if settings.get("choices", None):
            arg_info["choices"] = sorted(list(settings["choices"]))
        if settings.get("id_part", None):
            arg_info["id_part"] = settings["id_part"]
        if settings.get("nargs", None):
            arg_info["nargs"] = settings["nargs"]
        if settings.get("completer", None):
            arg_info["has_completer"] = True
        if settings.get("default", None):
            if not isinstance(settings["default"], (float, int, str, list, bool)):
                arg_info["default"] = str(settings["default"])
            else:
                arg_info["default"] = settings["default"]
        
        arg_info["desc"] = settings.get("help", "")
        help_info['arguments'][arg_name] = arg_info

    return help_info


def build_command_group_help_info(name: str, command_group=None, command_table=None, group_table=None):
    """Build comprehensive help information for a command group.
    
    Args:
        name: Command group name
        command_group: Command group object (optional)
        command_table: Command table for resolving subcommands (optional)
        group_table: Group table for resolving subgroups (optional)
        
    Returns:
        dict: Complete command group help information including subcommands and subgroups
    """
    if command_group is None:
        return {"short-summary": "Command group not found"}
    
    help_info = get_command_help_info(name, command_group)
    
    # Add subcommands if command_table is provided
    if command_table:
        help_info['subcommands'] = {
            cmd_name: get_command_help_info(cmd_name, cmd) 
            for cmd_name, cmd in command_table.items() 
            if cmd_name.startswith(name + ' ')
        }
    
    # Add subgroups if group_table is provided
    if group_table:
        help_info['subgroups'] = {
            group_name: get_command_help_info(group_name, group) 
            for group_name, group in group_table.items() 
            if group_name.startswith(name + ' ')
        }
    
    return help_info


def handle_aaz_type(aaz_type: AAZBaseType):
    """Convert AAZ type to JSON schema representation.
    
    Args:
        aaz_type: AAZ type to convert
        
    Returns:
        dict: JSON schema representation of the type
    """
    # Get the base schema first
    schema = _get_base_schema_for_type(aaz_type)
    
    # Handle nullable types by adding "null" to the type array
    if hasattr(aaz_type, '_nullable') and aaz_type._nullable:
        if "type" in schema:
            # Convert single type to array if needed
            if isinstance(schema["type"], str):
                schema["type"] = [schema["type"], "null"]
            elif isinstance(schema["type"], list) and "null" not in schema["type"]:
                schema["type"].append("null")
        else:
            # For complex schemas without a simple type (like empty schema for any type)
            # we fall back to oneOf approach
            return {
                "oneOf": [
                    schema,
                    {"type": "null"}
                ]
            }
    
    return schema


def _get_base_schema_for_type(aaz_type: AAZBaseType):
    """Get the base JSON schema for an AAZ type without nullable handling.
    
    Args:
        aaz_type: AAZ type to convert
        
    Returns:
        dict: Base JSON schema representation
    """
    if isinstance(aaz_type, AAZObjectType):
        schema = {
            "type": "object",
            "properties": {}
        }
        # Process each field in the object
        for field_name, field_type in aaz_type._fields.items():
            field_schema = handle_aaz_type(field_type)

            # Add description from various possible sources
            description = None
            if hasattr(field_type, '_help') and field_type._help:
                if isinstance(field_type._help, dict):
                    description = field_type._help.get('short-summary') or field_type._help.get('description')
                else:
                    description = str(field_type._help)
            if description:
                field_schema["description"] = description
            # Add serialized name if different from field name
            if hasattr(field_type, '_serialized_name') and field_type._serialized_name and field_type._serialized_name != field_name:
                if "description" in field_schema:
                    field_schema["description"] += f" (serialized as: {field_type._serialized_name})"
                else:
                    field_schema["description"] = f"Serialized as: {field_type._serialized_name}"
            
            schema["properties"][field_name] = field_schema
        # For simplicity, we don't mark any fields as required by default
        # This can be enhanced based on specific requirements
        return schema
    elif isinstance(aaz_type, AAZDictType):
        element_schema = handle_aaz_type(aaz_type.Element)
        schema = {
            "type": "object",
            "additionalProperties": element_schema
        }
        return schema
    elif isinstance(aaz_type, AAZListType):
        element_schema = handle_aaz_type(aaz_type.Element)
        schema = {
            "type": "array",
            "items": element_schema
        }
        return schema
    elif isinstance(aaz_type, AAZIntType):
        schema = {"type": "integer"}
        if isinstance(aaz_type, AAZIntArg):
            if aaz_type._default is not None and not isinstance(aaz_type._default, _AAZUndefinedType):
                schema["default"] = aaz_type._default
            if aaz_type._help:
                schema["description"] = aaz_type._help
        return schema
    elif isinstance(aaz_type, AAZBoolType):
        schema = {"type": "boolean"}
        if isinstance(aaz_type, AAZBoolArg):
            if aaz_type._default is not None and not isinstance(aaz_type._default, _AAZUndefinedType):
                schema["default"] = aaz_type._default
            if aaz_type._help:
                schema["description"] = aaz_type._help
        return schema
    elif isinstance(aaz_type, AAZStrType):
        schema = {"type": "string"}
        if isinstance(aaz_type, AAZStrArg):
            if aaz_type._default is not None and not isinstance(aaz_type._default, _AAZUndefinedType):
                schema["default"] = aaz_type._default
            if aaz_type._help:
                schema["description"] = aaz_type._help
        return schema
    elif isinstance(aaz_type, AAZFloatType):
        schema = {"type": "number"}
        if isinstance(aaz_type, AAZFloatArg):
            if aaz_type._default is not None and not isinstance(aaz_type._default, _AAZUndefinedType):
                schema["default"] = aaz_type._default
        return schema
    elif isinstance(aaz_type, AAZAnyType):
        # Any type can be any JSON value - use empty schema which allows anything
        if isinstance(aaz_type, AAZBaseArg):
            schema = {}
            if aaz_type._default is not None and not isinstance(aaz_type._default, _AAZUndefinedType):
                schema["default"] = aaz_type._default
            if aaz_type._help:
                schema["description"] = aaz_type._help
        return schema
    else:
        # Handle unknown types as any type
        logger.warning("Unknown AAZ type encountered: %s, treating as any type", type(aaz_type).__name__)
        return {}

def handle_arg_schema(arg_schema: AAZArgumentsSchema):
    """Convert AAZ arguments schema to JSON schema representation.
    
    Args:
        arg_schema: AAZ arguments schema to convert
        
    Returns:
        dict: JSON schema representation of the arguments schema
    """
    # AAZArgumentsSchema inherits from AAZObjectType, so we can reuse the logic
    return handle_aaz_type(arg_schema)


def handle_help_schema(help_info):
    argument_info = help_info['arguments']
    properties = {}
    required = []
    for _, arg_info in argument_info.items():
        arg_dict = {
            "name": arg_info["name"],
        }
        if arg_info.get("type"):
            arg_dict["type"] = arg_info["type"]
        if arg_info.get("required", False):
            required.append(arg_info["name"])
        if arg_info.get("desc"):
            arg_dict["description"] = arg_info["desc"]
        if arg_info.get("default") is not None:
            arg_dict["default"] = arg_info["default"]
        if arg_info.get("options"):
            arg_dict["options"] = [str(option) for option in arg_info["options"]] if arg_info["options"] else []
        if arg_info.get("choices"):
            arg_dict["enum"] = arg_info["choices"]
        properties[arg_info["name"]] = arg_dict
    return {
        "type": "object",
        "properties": properties,
        "required": required
    }
