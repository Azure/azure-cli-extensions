# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from knack.log import get_logger

logger = get_logger(__name__)


def interactive(func):
    """
    Decorator to wrap all promptable functions below
    :param func:
    :return:
    """

    def function_wrapper(*args, **kwargs):
        # if os.get("AZURE_DISABLE_CONFIRM_PROMPT"):
        #    raise NoTTYException
        return func(*args, **kwargs)

    return function_wrapper


@interactive
def prompt_y_n(msg):
    """
    Prompts [y/n] to the user with the given message.
    """
    from knack.prompting import prompt_y_n as _prompt_y_n

    return _prompt_y_n(msg)


@interactive
def prompt(msg):
    """
    Basic prompt to the user with the given message.
    """
    from knack.prompting import prompt as _prompt

    return _prompt(msg)


@interactive
def prompt_assert(msg):
    """
    Prompts to the user with the given message and forces them to enter it.
    """
    from knack.prompting import prompt as _prompt

    while True:
        result = _prompt(msg)
        if result:
            return result


@interactive
def prompt_pass(msg, confirm=False, allow_empty=True):
    """
    Prompts to the user with the given message and masks the input.
    """
    from knack.prompting import prompt_pass as _prompt_pass

    while True:
        password = _prompt_pass(msg, confirm)
        if password or allow_empty:
            return password
        logger.warning("Password must not be empty.")


@interactive
def prompt_for_input(question, default=None, padding=True, strip=True):
    """
    More complex prompt to the user with default value and ability to control
    white space.
    """
    from humanfriendly.prompts import prompt_for_input as _prompt_for_input

    return _prompt_for_input(question, default, padding, strip)


@interactive
def prompt_for_choice(choices, default=None, padding=True):
    """
    Gives the user choices in a prompt.
    """
    from humanfriendly.prompts import prompt_for_choice as _prompt_for_choice

    return _prompt_for_choice(choices, default, padding)
