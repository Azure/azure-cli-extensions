# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=import-error

import re
import shlex

from knack.util import CLIError

from jinja2 import Template
from azext_alias._const import (
    POS_ARG_NAME_REGEX,
    NUMBER_PLACEHOLDER_REGEX,
    DUPLICATED_PLACEHOLDER_ERROR,
    RENDER_TEMPLATE_ERROR,
    INSUFFICIENT_POS_ARG_ERROR,
    PLACEHOLDER_EVAL_ERROR,
    EXPRESSION_REGEX
)


def get_pos_args_names(arg):
    """
    Get all the positional arguments' names in order.

    Args:
        arg: The word which this function performs searching on.

    Returns:
        A list of positional arguments' names.
    """
    pos_args_name = list(map(str.strip, re.findall(POS_ARG_NAME_REGEX, arg)))

    # Make sure there is no duplicated positional argument
    if len(pos_args_name) != len(set(pos_args_name)):
        raise CLIError(DUPLICATED_PLACEHOLDER_ERROR.format(arg))

    for i, pos_arg_name in enumerate(pos_args_name):
        if pos_arg_name.isdigit():
            pos_args_name[i] = '_{}'.format(pos_arg_name)

    return pos_args_name


def stringify_placeholder_expr(arg):
    """
    Jinja does not accept numbers as placeholder names,
    so add a "_" before the number to make them valid placeholder names.
    Surround placeholders expressions with "" so we can preserve spaces inside the positional arguments.

    Args:
        arg: The string to process.

    Returns:
        A processed string where placeholders are surrounded by "" and
        numbered placeholders are prepended with "_".
    """
    number_placeholders = list(map(str.strip, re.findall(NUMBER_PLACEHOLDER_REGEX, arg)))
    for number_placeholder in number_placeholders:
        number = re.search(r'\d+', number_placeholder).group()
        arg = arg.replace(number_placeholder, '{{_' + number + '}}')

    return arg.replace('{{', '"{{').replace('}}', '}}"')


def build_pos_args_table(full_alias, args, start_index):
    """
    Build a dictionary of position argument.

    Args:
        full_alias: The full alias (including any placeholders).
        args: The arguments that the user inputs in the terminal.
        start_index: The index at which we start taking position arguments.
    Returns:
        A dictionary with the key beign the name of the placeholder and its value
        being the respective positional argument.
    """
    pos_args_placeholder = get_pos_args_names(full_alias)
    pos_args = args[start_index: start_index + len(pos_args_placeholder)]

    if len(pos_args_placeholder) != len(pos_args):
        error_msg = INSUFFICIENT_POS_ARG_ERROR.format(full_alias,
                                                      len(pos_args_placeholder),
                                                      '' if len(pos_args_placeholder) == 1 else 's',
                                                      len(pos_args))
        raise CLIError(error_msg)

    # Escape '"' because we are using "" to surround placeholder expressions
    for i, pos_arg in enumerate(pos_args):
        pos_args[i] = pos_arg.replace('"', '\\"')

    return dict(zip(pos_args_placeholder, pos_args))


def render_template(cmd_derived_from_alias, pos_args_table):
    """
    Render cmd_derived_from_alias as a Jinja template with pos_args_table as the arguments.

    Args:
        cmd_derived_from_alias: The string to be injected with positional arguemnts.
        pos_args_table: The dictionary used to rendered.
    Returns:
        A processed string with positional arguments injected.
    """
    try:
        cmd_derived_from_alias = stringify_placeholder_expr(cmd_derived_from_alias)
        template = Template(cmd_derived_from_alias)

        # Shlex.split allows us to split a string by spaces while preserving quoted substrings
        # (positional arguments in this case)
        rendered = shlex.split(template.render(pos_args_table))

        # Manually check if there is any runtime error (such as index out of range)
        # since jinja2 only checks for compile error
        # Only check for runtime errors if there is an empty string in rendered
        if '' in rendered:
            check_runtime_errors(cmd_derived_from_alias, pos_args_table)

        return rendered
    except Exception as exception:
        if isinstance(exception, CLIError):
            raise

        # Template has compile error
        split_exception_message = str(exception).split()

        # Check if the error message provides the index of the erroneous character
        error_index = split_exception_message[-1]
        if error_index.isdigit():
            split_exception_message.insert(-1, 'index')
            error_msg = RENDER_TEMPLATE_ERROR.format(' '.join(split_exception_message), cmd_derived_from_alias)

            # Calculate where to put an arrow (^) char so that it is exactly below the erroneous character
            # e.g. ... "{{a.split('|)}}"
            #                       ^
            error_msg += '\n{}^'.format(' ' * (len(error_msg) - len(cmd_derived_from_alias) + int(error_index) - 1))
        else:
            exception_str = str(exception).replace('"{{', '}}').replace('}}"', '}}')
            error_msg = RENDER_TEMPLATE_ERROR.format(cmd_derived_from_alias, exception_str)

        raise CLIError(error_msg)


def check_runtime_errors(cmd_derived_from_alias, pos_args_table):
    """
    Validate placeholders and their expressions in cmd_derived_from_alias to make sure
    that there is no runtime error (such as index out of range).

    Args:
        cmd_derived_from_alias:
        pos_args_table:
    """
    for placeholder, value in pos_args_table.items():
        exec('{} = "{}"'.format(placeholder, value))  # pylint: disable=exec-used

    expressions = list(map(str.strip, re.findall(EXPRESSION_REGEX, cmd_derived_from_alias)))
    for expression in expressions:
        try:
            exec(expression)  # pylint: disable=exec-used
        except Exception as exception:  # pylint: disable=broad-except
            error_msg = PLACEHOLDER_EVAL_ERROR.format(expression, exception)
            raise CLIError(error_msg)
