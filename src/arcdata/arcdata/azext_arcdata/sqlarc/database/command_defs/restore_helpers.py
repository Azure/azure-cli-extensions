# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------
import pydash as _
import copy
import time

from azext_arcdata.core.exceptions import CLIError


def create_new_database_model_to_restore_to(arm_model, source, time, name):
    new_database = copy.deepcopy(arm_model)
    new_database.properties.create_mode = "restorePointInTime"
    new_database.properties.source_database_id = source
    new_database.properties.restore_point_in_time = time
    new_database.id = generate_new_id_from_new_name(arm_model.id, name)
    new_database.name = name
    new_database.properties.backup_information = None
    new_database.system_data = None
    new_database.properties.provisioning_state = None
    new_database.properties.database_creation_date = None
    return new_database


def generate_new_id_from_new_name(id, name):
    segments = id.split("/")
    segments[-1] = name
    return "/".join(segments)


# Returns an Error if it failed, False if it is not complete, True if the Restore is complete
def poll_restore_status(client, resource_group, full_instance_name, dest_name):
    poll_count = 0
    arm_model = client.services.sqlarc.get_database_config(
        resource_group, full_instance_name, dest_name
    )
    while (
        poll_count < 10
        and arm_model.properties.provisioning_state != "Succeeded"
    ):
        time.sleep(6)
        arm_model = client.services.sqlarc.get_database_config(
            resource_group, full_instance_name, dest_name
        )
        state = arm_model.properties.provisioning_state
        if state == "Succeeded" or state == "Processing":
            return True
        elif state == "Canceled" or state == "Failed":
            break
        else:
            poll_count += 1
        if poll_count % 3 == 0:
            client.stdout(
                "The restore request has been made, waiting for status of the request..."
            )
    if (
        arm_model.properties.provisioning_state == "Succeeded"
        or state == "Processing"
    ):
        return
    raise CLIError(
        'Status of restore request is: "{0}". Please look at logs for more information.'.format(
            arm_model.properties.provisioning_state
        )
    )
