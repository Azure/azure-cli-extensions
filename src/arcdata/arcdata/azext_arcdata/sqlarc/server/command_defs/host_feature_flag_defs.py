# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------
from knack.log import get_logger
from azext_arcdata.sqlarc.server.command_defs.host_feature_flag_helpers import (
    is_feature_flag_present,
    delete_feature_flag,
    show_feature_flag,
    update_feature_flag
)
from azext_arcdata.sqlarc.common.helpers import get_machine_name
from azext_arcdata.core.exceptions import CLIError

logger = get_logger(__name__)


def feature_flag_set(client, **kwargs):
    """
    This function is responsible for settings feature flag.
    """
    try:
        # Get Values from given arguments

        cvo = client.args_to_command_value_object(kwargs)
        machineName = get_machine_name(client)
        current_config = client.services.sqlarc.get_server_config(
            cvo.resource_group, machineName
        )

        updated_config = update_feature_flag(
            current_config, cvo.name, cvo.enable
        )

        client.services.sqlarc.put_server_config(
            cvo.resource_group, machineName, updated_config
        )

        message = "{0} feature flag successfully updated to {1}"
        client.stdout(message.format(cvo.name, cvo.enable))

    except Exception as e:
        logger.info(e)
        raise CLIError(e)


def feature_flag_delete(client, **kwargs):
    """
    This function is responsible for deleting feature flag.
    """
    try:
        # Get Values from given arguments
        cvo = client.args_to_command_value_object(kwargs)
        machineName = get_machine_name(client)
        current_config = client.services.sqlarc.get_server_config(
            cvo.resource_group, machineName
        )

        if not is_feature_flag_present(current_config, cvo.name):
            message = "Feature flag not found for {0}."
            client.stdout(message.format(cvo.name))
            return

        updated_config = delete_feature_flag(current_config, cvo.name)
        client.services.sqlarc.put_server_config(
            cvo.resource_group, machineName, updated_config
        )

        message = "{0} feature flag deleted successfully."
        client.stdout(message.format(cvo.name))

    except Exception as e:
        logger.info(e)
        raise CLIError(e)


def feature_flag_show(client, **kwargs):
    """
    This function is responsible for displaying feature flag.
    """
    try:
        # Get Values from given arguments
        cvo = client.args_to_command_value_object(kwargs)
        machineName = get_machine_name(client)
        current_config = client.services.sqlarc.get_server_config(
            cvo.resource_group, machineName
        )

        feature_flag = show_feature_flag(current_config, cvo.name)
        if feature_flag is None or not feature_flag:
            if cvo.name is None:
                client.stdout("No feature flags are set for this machine.")
            else:
                message = "Feature flag not found for {0}."
                client.stdout(message.format(cvo.name))

            return None

        return feature_flag

    except Exception as e:
        logger.info(e)
        raise CLIError(e)
