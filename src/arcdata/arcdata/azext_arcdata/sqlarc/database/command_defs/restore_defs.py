# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------
from knack.log import get_logger
from azext_arcdata.sqlarc.common.validators import (
    validate_fci_is_inactive,
    validate_license_type,
)
from azext_arcdata.sqlarc.database.command_defs.restore_helpers import (
    create_new_database_model_to_restore_to,
    poll_restore_status
)
from azext_arcdata.sqlarc.database.validators import (
    validate_backups_are_active,
    validate_time
)
from azext_arcdata.core.exceptions import CLIError
from datetime import datetime, timezone

now_utc = datetime.now(timezone.utc)
logger = get_logger(__name__)


def restore(client):
    try:
        # Get Values from given arguments
        cvo = client.args_to_command_value_object()

        # Create a datetime object representing the current date and time if not time was given
        pitr_time = datetime.now(timezone.utc) if cvo.time is None else cvo.time

        full_instance_name = cvo.server.replace("/", "_")

        # Need to get Instance model to find the Server model to get the license type
        instance_arm_model = client.services.sqlarc.get_instance_config(
            cvo.resource_group, full_instance_name
        )
        # Verify the user has the appropriate license type to execute this command
        license = client.services.sqlarc.get_license_type(
            instance_arm_model.properties.container_resource_id
        )
        validate_license_type(license)

        validate_fci_is_inactive(instance_arm_model)

        # We want to get a 404 Error here as it means the database does not exist, and if it does exist we want to create an error saying that the database already exists.
        try:
            arm_model = client.services.sqlarc.get_database_config(
                cvo.resource_group, full_instance_name, cvo.dest_name
            )
            raise Exception(
                "Destination database already exists, please select a new destination database name."
            )
        except Exception as e:
            if (
                "Destination database already exists, please select a new destination database name."
                == str(e)
            ):
                raise (e)

        arm_model = client.services.sqlarc.get_database_config(
            cvo.resource_group, full_instance_name, cvo.name
        )

        validate_backups_are_active(
            instance_arm_model.properties.backup_policy,
            arm_model.properties.backup_policy,
        )

        validate_time(arm_model.properties.backup_information, cvo.time)

        new_database = create_new_database_model_to_restore_to(
            arm_model, cvo.name, pitr_time, cvo.dest_name
        )
        client.services.sqlarc.create_sqlarc_database(
            cvo.resource_group, full_instance_name, cvo.dest_name, new_database
        )

        # Poll the Status of the Restore
        poll_restore_status(
            client, cvo.resource_group, full_instance_name, cvo.dest_name
        )
        client.stdout(
            "The restore request has successfully been sent to the Sql Database."
        )

    except Exception as e:
        logger.info(e)
        raise CLIError(e)
