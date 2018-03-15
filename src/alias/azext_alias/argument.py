# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=import-error

import re
import shlex

from knack.util import CLIError

import jinja2 as jinja
from azext_alias._const import (
    DUPLICATED_PLACEHOLDER_ERROR,
    RENDER_TEMPLATE_ERROR,
    INSUFFICIENT_POS_ARG_ERROR,
    PLACEHOLDER_EVAL_ERROR,
    PLACEHOLDER_BRACKETS_ERROR
)


def get_placeholders(arg, check_duplicates=False):
    """
    Get all the placeholders' names in order.
    Use the regex below to locate all the opening ({{) and closing brackets (}}).
    After that, extract "stuff" inside the brackets.

    Args:
        arg: The word which this function performs searching on.
        check_duplicates: True if we want to check for duplicated positional arguments.

    Returns:
        A list of positional arguments in order.
    """
    placeholders = []
    last_match = None
    arg = normalize_placeholders(arg)
    for cur_match in re.finditer(r'\s*{{|}}\s*', arg):
        matched_text = cur_match.group().strip()
        if not last_match and matched_text == '{{':
            last_match = cur_match
            continue

        last_matched_text = '' if not last_match else last_match.group().strip()
        # Check if the positional argument is enclosed with {{ }} properly
        if (not last_matched_text and matched_text == '}}') or (last_matched_text == '{{' and matched_text != '}}'):
            raise CLIError(PLACEHOLDER_BRACKETS_ERROR.format(arg))
        elif last_matched_text == '{{' and matched_text == '}}':
            # Extract start and end index of the placeholder name
            start_index, end_index = last_match.span()[1], cur_match.span()[0]
            placeholders.append(arg[start_index: end_index].strip())
            last_match = None

    # last_match did not reset - that means brackets are not enclosed properly
    if last_match:
        raise CLIError(PLACEHOLDER_BRACKETS_ERROR.format(arg))

    # Make sure there is no duplicated placeholder names
    if check_duplicates and len(placeholders) != len(set(placeholders)):
        raise CLIError(DUPLICATED_PLACEHOLDER_ERROR.format(arg))

    return placeholders


def normalize_placeholders(arg, inject_quotes=False):
    """
    Normalize placeholders' names so that the template can be ingested into Jinja template engine.
    - Jinja does not accept numbers as placeholder names, so add a "_"
        before the numbers to make them valid placeholder names.
    - Surround placeholders expressions with "" so we can preserve spaces inside the positional arguments.

    Args:
        arg: The string to process.
        inject_qoutes: True if we want to surround placeholders with a pair of quotes.

    Returns:
        A processed string where placeholders are surrounded by "" and
        numbered placeholders are prepended with "_".
    """
    number_placeholders = re.findall(r'{{\s*\d+\s*}}', arg)
    for number_placeholder in number_placeholders:
        number = re.search(r'\d+', number_placeholder).group()
        arg = arg.replace(number_placeholder, '{{_' + number + '}}')

    return arg.replace('{{', '"{{').replace('}}', '}}"') if inject_quotes else arg


def build_pos_args_table(full_alias, args, start_index):
    """
    Build a dictionary where the key is placeholder name and the value is the position argument value.

    Args:
        full_alias: The full alias (including any placeholders).
        args: The arguments that the user inputs in the terminal.
        start_index: The index at which we start ingesting position arguments.

    Returns:
        A dictionary with the key beign the name of the placeholder and its value
        being the respective positional argument.
    """
    pos_args_placeholder = get_placeholders(full_alias, check_duplicates=True)
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
        cmd_derived_from_alias = normalize_placeholders(cmd_derived_from_alias, inject_quotes=True)
        template = jinja.Template(cmd_derived_from_alias)

        # Shlex.split allows us to split a string by spaces while preserving quoted substrings
        # (positional arguments in this case)
        rendered = shlex.split(template.render(pos_args_table))

        # Manually check if there is any runtime error (such as index out of range)
        # since Jinja template engine only checks for compile time error.
        # Only check for runtime errors if there is an empty string in rendered.
        if '' in rendered:
            check_runtime_errors(cmd_derived_from_alias, pos_args_table)

        return rendered
    except Exception as exception:
        # Exception raised from runtime error
        if isinstance(exception, CLIError):
            raise

        # The template has some sort of compile time errors
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
        cmd_derived_from_alias: The command derived from the alias
            (include any positional argument placehodlers)
        pos_args_table: The positional argument table.
    """
    for placeholder, value in pos_args_table.items():
        exec('{} = "{}"'.format(placeholder, value))  # pylint: disable=exec-used

    expressions = get_placeholders(cmd_derived_from_alias)
    for expression in expressions:
        try:
            exec(expression)  # pylint: disable=exec-used
        except Exception as exception:  # pylint: disable=broad-except
            error_msg = PLACEHOLDER_EVAL_ERROR.format(expression, exception)
            raise CLIError(error_msg)
