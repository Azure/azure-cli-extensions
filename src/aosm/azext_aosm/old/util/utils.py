# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Utility functions."""


def input_ack(ack: str, request_to_user: str) -> bool:
    """
    Overarching function to request, sanitise and return True if input is specified ack.

    This prints the question string and asks for user input. which is santised by
    removing all whitespaces in the string, and made lowercase. True is returned if the
    user input is equal to supplied acknowledgement string and False if anything else
    """
    unsanitised_ans = input(request_to_user)
    return str(unsanitised_ans.strip().replace(" ", "").lower()) == ack


def snake_case_to_camel_case(text):
    """Converts snake case to camel case."""
    components = text.split("_")
    return components[0] + "".join(
        x[0].upper() + x[1:] for x in components[1:]
    )
