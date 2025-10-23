# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------


def convert_string_to_bool(s):
    """
    Converts a string to a boolean value.
    """

    if s.casefold() == "true":
        return True
    elif s.casefold() == "false":
        return False


def get_machine_name(client):
    """
    Returns the arc server machine name of the client.
    """

    cvo = client.args_to_command_value_object()

    if cvo.sql_server_arc_name and cvo.machine_name:
        calculated_machine_name = client.services.sqlarc.get_instance_host_name(
            cvo.resource_group, cvo.sql_server_arc_name
        )

        if calculated_machine_name != cvo.machine_name:
            raise ValueError(
                "Values provided for 'sql-server-arc-name' and 'machine-name' does not match."
            )

    if not cvo.machine_name:
        return client.services.sqlarc.get_instance_host_name(
            cvo.resource_group, cvo.sql_server_arc_name
        )
    return cvo.machine_name
