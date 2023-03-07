# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=unused-import
# pylint: disable=too-many-statements

from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import (
    get_enum_type,
    tags_type,
    get_three_state_flag,
)
from azure.cli.core.commands.validators import (
    validate_file_or_dict,
)
from azext_devcenter.action import (
    AddEmailNotification,
    AddWebhookNotification,
)

from ._validators import validate_dev_box_list, validate_time


dev_center_type = CLIArgumentType(
    options_list=["--dev-center-name", "--dev-center", "-d"],
    help='The name of the dev center. Use az configure -d dev-center=<dev_center_name> to configure a default.',
    configured_default='dev-center')

project_type = CLIArgumentType(
    options_list=["--project", "--project-name"],
    help='The name of the project. Use az configure -d project=<project_name> to configure a default.',
    configured_default='project')


def load_arguments(self, _):

    with self.argument_context("devcenter dev project list") as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )

    with self.argument_context("devcenter dev project show") as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            options_list=["--name", "-n"],
            type=str,
            help="The DevCenter " "Project upon which to execute operations.",
        )

    with self.argument_context("devcenter dev pool list") as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            arg_type=project_type,
        )

    with self.argument_context("devcenter dev pool show") as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            arg_type=project_type,
        )
        c.argument(
            "pool_name",
            options_list=["--name", "-n", "--pool-name"],
            type=str,
            help="The name of a pool of " "Dev Boxes.",
        )

    with self.argument_context("devcenter dev schedule list") as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            arg_type=project_type,
        )
        c.argument(
            "pool_name",
            options_list=["--pool-name", "--pool"],
            type=str,
            help="The name of a pool of Dev Boxes.",
        )

    with self.argument_context("devcenter dev schedule show") as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            arg_type=project_type,
        )
        c.argument(
            "pool_name",
            options_list=["--pool-name", "--pool"],
            type=str,
            help="The name of a pool of Dev Boxes.",
        )
        c.argument(
            "schedule_name",
            options_list=["--name", "-n", "--schedule-name"],
            type=str,
            help="The name of a " "schedule.",
        )

    with self.argument_context(
        "devcenter dev dev-box list", validator=validate_dev_box_list
    ) as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            arg_type=project_type,
        )
        c.argument(
            "user_id",
            type=str,
            help="The id of the user. If value is 'me', the identity is taken from the "
            "authentication context",
        )

    with self.argument_context("devcenter dev dev-box show") as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            arg_type=project_type,
        )
        c.argument(
            "user_id",
            type=str,
            help="The id of the user. If value is 'me', the identity is taken from the "
            "authentication context",
        )
        c.argument(
            "dev_box_name",
            options_list=["--name", "-n", "--dev-box-name"],
            type=str,
            help="The name of a Dev " "Box.",
        )

    with self.argument_context("devcenter dev dev-box create") as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            arg_type=project_type,
        )
        c.argument(
            "user_id",
            type=str,
            help="The id of the user. If value is 'me', the identity is taken from the "
            "authentication context",
        )
        c.argument(
            "dev_box_name",
            options_list=["--name", "-n", "--dev-box-name"],
            type=str,
            help="The name of a Dev " "Box.",
        )
        c.argument(
            "pool_name",
            options_list=["--pool-name", "--pool"],
            type=str,
            help="The name of the Dev Box pool this machine belongs to.",
        )
        c.argument(
            "local_administrator",
            arg_type=get_enum_type(["Enabled", "Disabled"]),
            help="Indicates whether the "
            "owner of the Dev Box is a local administrator.",
        )

    with self.argument_context("devcenter dev dev-box delete") as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            arg_type=project_type,
        )
        c.argument(
            "user_id",
            type=str,
            help="The id of the user. If value is 'me', the identity is taken from the "
            "authentication context",
        )
        c.argument(
            "dev_box_name",
            options_list=["--name", "-n", "--dev-box-name"],
            type=str,
            help="The name of a Dev " "Box.",
        )

    with self.argument_context("devcenter dev dev-box show-remote-connection") as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            arg_type=project_type,
        )
        c.argument(
            "user_id",
            type=str,
            help="The id of the user. If value is 'me', the identity is taken from the "
            "authentication context",
        )
        c.argument(
            "dev_box_name",
            options_list=["--name", "-n", "--dev-box-name"],
            type=str,
            help="The name of a Dev " "Box.",
        )

    with self.argument_context("devcenter dev dev-box start") as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            arg_type=project_type,
        )
        c.argument(
            "user_id",
            type=str,
            help="The id of the user. If value is 'me', the identity is taken from the "
            "authentication context",
        )
        c.argument(
            "dev_box_name",
            options_list=["--name", "-n", "--dev-box-name"],
            type=str,
            help="The name of a Dev " "Box.",
        )

    with self.argument_context("devcenter dev dev-box stop") as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            arg_type=project_type,
        )
        c.argument(
            "user_id",
            type=str,
            help="The id of the user. If value is 'me', the identity is taken from the "
            "authentication context",
        )
        c.argument(
            "dev_box_name",
            options_list=["--name", "-n", "--dev-box-name"],
            type=str,
            help="The name of a Dev " "Box.",
        )
        c.argument(
            "hibernate",
            arg_type=get_three_state_flag(),
            help="Optional parameter to hibernate the dev box.",
        )

    with self.argument_context("devcenter dev dev-box delay-upcoming-action", validator=validate_time) as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            arg_type=project_type,
        )
        c.argument(
            "user_id",
            type=str,
            help="The AAD object id of the user. If value is 'me', the identity is taken "
            "from the authentication context.",
        )
        c.argument(
            "dev_box_name",
            options_list=["--name", "-n", "--dev-box-name"],
            type=str,
            help="The name of a Dev " "Box.",
        )
        c.argument("upcoming_action_id", type=str,
                   help="The upcoming action id.")
        c.argument(
            "delay_time", help="The delayed timespan from the most recent scheduled time. Format HH:MM")

    with self.argument_context("devcenter dev dev-box list-upcoming-action") as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            arg_type=project_type,
        )
        c.argument(
            "user_id",
            type=str,
            help="The AAD object id of the user. If value is 'me', the identity is taken "
            "from the authentication context.",
        )
        c.argument(
            "dev_box_name",
            options_list=["--name", "-n", "--dev-box-name"],
            type=str,
            help="The name of a Dev " "Box.",
        )

    with self.argument_context("devcenter dev dev-box show-upcoming-action") as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            arg_type=project_type,
        )
        c.argument(
            "user_id",
            type=str,
            help="The AAD object id of the user. If value is 'me', the identity is taken "
            "from the authentication context.",
        )
        c.argument(
            "dev_box_name",
            options_list=["--name", "-n", "--dev-box-name"],
            type=str,
            help="The name of a Dev " "Box.",
        )
        c.argument("upcoming_action_id", type=str,
                   help="The upcoming action id.")

    with self.argument_context("devcenter dev dev-box skip-upcoming-action") as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            arg_type=project_type,
        )
        c.argument(
            "user_id",
            type=str,
            help="The AAD object id of the user. If value is 'me', the identity is taken "
            "from the authentication context.",
        )
        c.argument(
            "dev_box_name",
            options_list=["--name", "-n", "--dev-box-name"],
            type=str,
            help="The name of a Dev " "Box.",
        )
        c.argument("upcoming_action_id", type=str,
                   help="The upcoming action id.")

    with self.argument_context("devcenter dev dev-box wait") as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            arg_type=project_type,
        )
        c.argument(
            "user_id",
            type=str,
            help="The id of the user. If value is 'me', the identity is taken from the "
            "authentication context",
        )
        c.argument(
            "dev_box_name",
            options_list=["--name", "-n", "--dev-box-name"],
            type=str,
            help="The name of a Dev " "Box.",
        )

    with self.argument_context("devcenter dev environment list") as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            arg_type=project_type,
        )
        c.argument(
            "user_id",
            type=str,
            help="The AAD object id of the user. If value is 'me', the identity is taken "
            "from the authentication context.",
        )

    with self.argument_context("devcenter dev environment show") as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            arg_type=project_type,
        )
        c.argument(
            "user_id",
            type=str,
            help="The id of the user. If value is 'me', the identity is taken from the "
            "authentication context",
        )
        c.argument(
            "environment_name",
            options_list=["--name", "-n", "--environment-name"],
            type=str,
            help="The name " "of the environment.",
        )

    with self.argument_context("devcenter dev environment create") as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            arg_type=project_type,
        )
        c.argument(
            "user_id",
            type=str,
            help="The id of the user. If value is 'me', the identity is taken from the "
            "authentication context",
        )
        c.argument(
            "environment_name",
            options_list=["--name", "-n", "--environment-name"],
            type=str,
            help="The name " "of the environment.",
        )
        c.argument("description", type=str,
                   help="Description of the Environment.")
        c.argument("catalog_name", type=str, required=True,
                   help="Name of the catalog.")
        c.argument(
            "catalog_item_name",
            type=str,
            required=True,
            help="Name of the catalog item.",
        )
        c.argument(
            "parameters",
            type=validate_file_or_dict,
            help="Parameters object for the deploy action Expected "
            "value: json-string/json-file/@json-file.",
        )
        c.argument("tags", tags_type)
        c.argument("environment_type", type=str, help="Environment type.")
        c.argument(
            "user", type=str, help="The AAD object id of the owner of this Environment."
        )

    with self.argument_context("devcenter dev environment update") as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            arg_type=project_type,
        )
        c.argument(
            "user_id",
            type=str,
            help="The id of the user. If value is 'me', the identity is taken from the "
            "authentication context. Default is 'me'",
        )
        c.argument(
            "environment_name",
            options_list=["--name", "-n", "--environment-name"],
            type=str,
            help="The name " "of the environment.",
        )
        c.argument("description", type=str,
                   help="Description of the Environment.")
        c.argument("catalog_name", type=str, help="Name of the catalog.")
        c.argument("catalog_item_name", type=str,
                   help="Name of the catalog item.")
        c.argument(
            "parameters",
            type=validate_file_or_dict,
            help="Parameters object for the deploy action Expected "
            "value: json-string/json-file/@json-file.",
        )
        c.argument(
            "scheduled_tasks",
            type=validate_file_or_dict,
            help="Set of supported scheduled tasks to help "
            "manage cost. Expected value: json-string/json-file/@json-file.",
        )
        c.argument("tags", tags_type)

    with self.argument_context("devcenter dev environment delete") as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            arg_type=project_type,
        )
        c.argument(
            "user_id",
            type=str,
            help="The id of the user. If value is 'me', the identity is taken from the "
            "authentication context",
        )
        c.argument(
            "environment_name",
            options_list=["--name", "-n", "--environment-name"],
            type=str,
            help="The name " "of the environment.",
        )

    with self.argument_context("devcenter dev environment wait") as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            arg_type=project_type,
        )
        c.argument(
            "user_id",
            type=str,
            help="The id of the user. If value is 'me', the identity is taken from the "
            "authentication context",
        )
        c.argument(
            "environment_name",
            options_list=["--name", "-n", "--environment-name"],
            type=str,
            help="The name " "of the environment.",
        )

    with self.argument_context("devcenter dev environment deploy-action") as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            type=str,
            help="The DevCenter Project upon which to execute operations.",
        )
        c.argument(
            "user_id",
            type=str,
            help="The AAD object id of the user. If value is 'me', the identity is taken "
            "from the authentication context",
        )
        c.argument(
            "environment_name",
            options_list=["--name", "-n", "--environment-name"],
            type=str,
            help="The name " "of the environment.",
        )
        c.argument("action_id", type=str,
                   help="The Catalog Item action id to execute")
        c.argument(
            "parameters",
            type=validate_file_or_dict,
            help="Parameters object for the Action Expected value: "
            "json-string/json-file/@json-file.",
        )

    with self.argument_context("devcenter dev catalog-item list") as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            arg_type=project_type,
        )

    with self.argument_context("devcenter dev catalog-item show") as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            arg_type=project_type,
        )
        c.argument(
            "catalog_item_id", type=str, help="The unique id of the catalog item."
        )

    with self.argument_context("devcenter dev catalog-item-version list") as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            arg_type=project_type,
        )
        c.argument(
            "catalog_item_id", type=str, help="The unique id of the catalog item."
        )

    with self.argument_context("devcenter dev catalog-item-version show") as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            arg_type=project_type,
        )
        c.argument(
            "catalog_item_id", type=str, help="The unique id of the catalog item."
        )
        c.argument("version", type=str,
                   help="The version of the catalog item.")

    with self.argument_context("devcenter dev environment-type list") as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            arg_type=project_type,
        )

    with self.argument_context("devcenter dev notification-setting create") as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            arg_type=project_type,
        )
        c.argument(
            "user_id",
            type=str,
            help="The AAD object id of the user. If value is 'me', the identity is taken "
            "from the authentication context.",
        )
        c.argument(
            "enabled",
            arg_type=get_three_state_flag(),
            help="If notification is enabled for the user.",
        )
        c.argument(
            "culture",
            type=str,
            help="The culture that MEO can accommdate requests to send emails in.",
        )
        c.argument(
            "boolean_enabled",
            arg_type=get_three_state_flag(),
            help="If notification is enabled for DevBox " "provisioning.",
            arg_group="Notification Type Dev Box Provisioning Notification",
        )
        c.argument(
            "email_notification",
            action=AddEmailNotification,
            nargs="+",
            help="The email notification",
            arg_group="Notification Type Dev Box Provisioning Notification Notification Channel",
        )
        c.argument(
            "webhook_notification",
            action=AddWebhookNotification,
            nargs="+",
            help="The webhook notification",
            arg_group="Notification Type Dev Box Provisioning Notification Notification Channel",
        )

    with self.argument_context("devcenter dev notification-setting show") as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            required=True,
            arg_type=project_type,
        )
        c.argument(
            "user_id",
            type=str,
            help="The AAD object id of the user. If value is 'me', the identity is taken "
            "from the authentication context.",
        )

    with self.argument_context(
        "devcenter dev notification-setting list-allowed-culture"
    ) as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            required=True,
            arg_type=project_type,
        )
        c.argument(
            "user_id",
            type=str,
            help="The AAD object id of the user. If value is 'me', the identity is taken "
            "from the authentication context.",
        )
