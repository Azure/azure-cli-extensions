# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------
from knack.log import get_logger
from azext_arcdata.sqlarc.server.command_defs.host_properties_helpers import *
from azext_arcdata.sqlarc.common.helpers import get_machine_name
from azext_arcdata.core.exceptions import CLIError

logger = get_logger(__name__)


def host_properties_set(client):
    """
    This function is responsible for setting common host level properties.
    """
    try:
        # Get Values from given arguments
        cvo = client.args_to_command_value_object()
        machineName = get_machine_name(client)
        current_config = client.services.sqlarc.get_server_config(
            cvo.resource_group, machineName
        )

        if is_settings_empty(current_config):
            raise ValueError(
                "Settings file is empty. Arc resource is in bad state."
            )

        if cvo.license_type:
            updated_config = update_license_type(
                current_config, cvo.license_type
            )

        if cvo.esu_enabled:
            updated_config = update_esu_enabled(current_config, cvo.esu_enabled)

        if cvo.skip_instances:
            updated_config = update_excluded_instances_list(
                current_config, cvo.skip_instances
            )

        client.services.sqlarc.put_server_config(
            cvo.resource_group, machineName, updated_config
        )

        message = "Host level properties successfully updated"
        client.stdout(message)

    except Exception as e:
        logger.info(e)
        raise CLIError(e)


def host_properties_show(client):
    """
    This function is responsible for displaying public settings of arc server.
    """
    try:
        # Get Values from given arguments
        cvo = client.args_to_command_value_object()
        machineName = get_machine_name(client)
        current_config = client.services.sqlarc.get_server_config(
            cvo.resource_group, machineName
        )

        # Print the value
        message = str(current_config["properties"]["settings"])
        client.stdout(message)

    except Exception as e:
        logger.info(e)
        raise CLIError(e)
