# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------
from knack.log import get_logger
from azext_arcdata.sqlarc.common.command_defs.backups_policy_helpers import *
from azext_arcdata.core.exceptions import CLIError

logger = get_logger(__name__)


def backups_policy_set(client, instance=None, database_name=None):
    try:
        # Get Values from given arguments
        cvo = client.args_to_command_value_object()

        full_instance_name = instance.replace("/", "_")

        # Make Get Request to Get Instance Config if we are targeting an Instance
        # and Request a databse if targeting a Database
        if not database_name:
            # Make Get Request to get Instance
            arm_model = client.services.sqlarc.get_instance_config(
                cvo.resource_group, full_instance_name
            )
            instance_arm_model = arm_model
        else:
            instance_arm_model = client.services.sqlarc.get_instance_config(
                cvo.resource_group, full_instance_name
            )
            arm_model = client.services.sqlarc.get_database_config(
                cvo.resource_group, full_instance_name, database_name
            )
        # note: The arm_model can be either a Database or Instance model, for our purposes
        # it does not matter which we are working with as they shapped the exact same way
        # Verify the user has the appropriate licensce type to execute this command
        license = client.services.sqlarc.get_license_type(
            instance_arm_model.properties.container_resource_id
        )
        validate_license_type(license)

        validate_fci_is_inactive(instance_arm_model)

        # Creates a New Backup Policy and replaced the existing one with it
        create_backups_policy_config(arm_model)
        apply_policy_changes_to_backups_policy(cvo, arm_model)

        if not database_name:
            client.services.sqlarc.put_instance_config(
                cvo.resource_group, full_instance_name, arm_model
            )
        else:
            arm_model = client.services.sqlarc.put_database_config(
                cvo.resource_group, full_instance_name, database_name, arm_model
            )

        # Display Success message :)
        success_message = (
            "The policy has successfully been sent to the Sql {0}."
        )
        if not database_name:
            client.stdout(success_message.format("Server instance"))
        else:
            client.stdout(success_message.format("Server database"))

    except Exception as e:
        logger.info(e)
        raise CLIError(e)


def backups_policy_show(client, instance=None, database_name=None):
    try:
        # Get Values from given arguments
        cvo = client.args_to_command_value_object()

        full_instance_name = instance.replace("/", "_")
        # Make Get Request to Get Instance Config if we are targeting an Instance
        # and Request a databse if targeting a Database
        if not database_name:
            # Make Get Request to get Instance
            arm_model = client.services.sqlarc.get_instance_config(
                cvo.resource_group, full_instance_name
            )
            instance_arm_model = arm_model
            policy_level = "Instance"
        else:
            instance_arm_model = client.services.sqlarc.get_instance_config(
                cvo.resource_group, full_instance_name
            )
            arm_model = client.services.sqlarc.get_database_config(
                cvo.resource_group, full_instance_name, database_name
            )
            policy_level = "Database"
        # note: The arm_model can be either a Database or Instance model, for our purposes
        # it does not matter which we are working with as they shapped the exact same way
        # Verify the user has the appropriate licensce type to execute this command
        license = client.services.sqlarc.get_license_type(
            instance_arm_model.properties.container_resource_id
        )
        validate_license_type(license)

        validate_fci_is_inactive(instance_arm_model)

        if not arm_model.properties.backup_policy and database_name:
            arm_model = instance_arm_model
            policy_level = "Instance"

        if not arm_model.properties.backup_policy:
            no_policy_message = (
                "No backup policy has been set for this Sql {0}."
            )
            if not database_name:
                client.stdout(no_policy_message.format("Server instance"))
            else:
                client.stdout(
                    no_policy_message.format(
                        "Server database or its corresponding Server instance"
                    )
                )
            return

        instance_name = instance_arm_model.properties.instance_name
        if instance_name == "MSSQLSERVER":
            instance_name = full_instance_name

        return displayable_backups_policy_config(
            arm_model, instance_name, database_name, policy_level
        )

    except Exception as e:
        logger.info(e)
        raise CLIError(e)


def backups_policy_delete(client, instance=None, database_name=None):
    try:
        # Get Values from given arguments
        cvo = client.args_to_command_value_object()

        full_instance_name = instance.replace("/", "_")

        # Make Get Request to Get Instance Config if we are targeting an Instance
        # and Request a databse if targeting a Database
        if not database_name:
            # Make Get Request to get Instance
            arm_model = client.services.sqlarc.get_instance_config(
                cvo.resource_group, full_instance_name
            )
            instance_arm_model = arm_model
        else:
            instance_arm_model = client.services.sqlarc.get_instance_config(
                cvo.resource_group, full_instance_name
            )
            arm_model = client.services.sqlarc.get_database_config(
                cvo.resource_group, full_instance_name, database_name
            )
        # note: The arm_model can be either a Database or Instance model, for our purposes
        # it does not matter which we are working with as they shapped the exact same way
        # Verify the user has the appropriate licensce type to execute this command
        license = client.services.sqlarc.get_license_type(
            instance_arm_model.properties.container_resource_id
        )
        validate_license_type(license)
        validate_fci_is_inactive(instance_arm_model)
        if not arm_model.properties.backup_policy:
            fail_message = (
                "There is no policy currently active on this Sql {0}."
            )
            if not database_name:
                client.stdout(fail_message.format("Server instance"))
            else:
                client.stdout(fail_message.format("Server database"))
            return

        if not cvo.yes:
            instance_name = instance_arm_model.properties.instance_name
            if not database_name:
                confirmation_dialogue = f"Deleting the backup policy for the instance will cause all databases in this instance that do not have their own database level backup policy set, to stop taking automated backups. Are you sure you want to delete the backup policy for the instance '{instance_name}'? [Y/N] "
            else:
                confirmation_dialogue = f"Deleting the backup policy for a the database will cause the database to use the instance's backup policy. If there is no instance backup policy set, there will no longer be any automated backups taken for the database. Are you sure you want to delete the backup policy for the database '{database_name}' on the instance '{instance_name}'?  [Y/N] "

            validAnswer = False
            user_input = input(confirmation_dialogue)
            while not validAnswer:
                answer = user_input.lower().strip()
                if answer == "n" or answer == "no":
                    client.stdout("Delete operation canceled.")
                    return
                elif answer == "y" or answer == "yes":
                    validAnswer = True
                else:
                    user_input = input("Please enter 'Y' or 'N': ")

        delete_backups_policy_config(arm_model)

        if not database_name:
            client.services.sqlarc.put_instance_config(
                cvo.resource_group, full_instance_name, arm_model
            )
        else:
            arm_model = client.services.sqlarc.put_database_config(
                cvo.resource_group, full_instance_name, database_name, arm_model
            )

        # Display Success message :)
        success_message = (
            "The policy has successfully been deleted from the Sql {0}."
        )
        if not database_name:
            client.stdout(success_message.format("Server instance"))
        else:
            client.stdout(success_message.format("Server database"))

    except Exception as e:
        logger.info(e)
        raise CLIError(e)
