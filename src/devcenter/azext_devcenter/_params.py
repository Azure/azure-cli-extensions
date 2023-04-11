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
    help="The name of the dev center. Use az configure -d dev-center=<dev_center_name> to configure a default.",
    configured_default="dev-center",
)

project_type = CLIArgumentType(
    options_list=["--project", "--project-name"],
    help="The name of the project. Use az configure -d project=<project_name> to configure a default.",
    configured_default="project",
)


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
            help="The AAD object id of the user. If value is 'me', the identity is taken from the "
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
            help="The AAD object id of the user. If value is 'me', the identity is taken from the "
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
            help="The AAD object id of the user. If value is 'me', the identity is taken from the "
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
            help="The AAD object id of the user. If value is 'me', the identity is taken from the "
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
            help="The AAD object id of the user. If value is 'me', the identity is taken from the "
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
            help="The AAD object id of the user. If value is 'me', the identity is taken from the "
            "authentication context",
        )
        c.argument(
            "dev_box_name",
            options_list=["--name", "-n", "--dev-box-name"],
            type=str,
            help="The name of a Dev " "Box.",
        )

    with self.argument_context("devcenter dev dev-box restart") as c:
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
            help="The AAD object id of the user. If value is 'me', the identity is taken from the "
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

    with self.argument_context(
        "devcenter dev dev-box delay-action", validator=validate_time
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
            help="The AAD object id of the user. If value is 'me', the identity is taken "
            "from the authentication context.",
        )
        c.argument(
            "dev_box_name",
            options_list=["--name", "-n", "--dev-box-name"],
            type=str,
            help="The name of a Dev " "Box.",
        )
        c.argument(
            "action_name",
            type=str,
            help="The name of an action that will take place on a Dev Box.",
        )
        c.argument(
            "delay_time",
            help="The delayed timespan from the most recent scheduled time. Format HH:MM",
        )

    with self.argument_context("devcenter dev dev-box delay-all-actions") as c:
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
        c.argument(
            "until", help="The time to delay the Dev Box action or actions until."
        )

    with self.argument_context("devcenter dev dev-box list-action") as c:
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

    with self.argument_context("devcenter dev dev-box show-action") as c:
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
        c.argument(
            "action_name",
            type=str,
            help="The name of an action that will take place on a Dev Box.",
        )

    with self.argument_context("devcenter dev dev-box skip-action") as c:
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
        c.argument(
            "action_name",
            type=str,
            help="The name of an action that will take place on a Dev Box.",
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
            help="The AAD object id of the user. If value is 'me', the identity is taken from the "
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
            help="The AAD object id of the user. If value is 'me', the identity is taken "
            "from the authentication context.",
        )
        c.argument(
            "environment_name",
            options_list=["--name", "-n", "--environment-name"],
            type=str,
            help="The name " "of the environment.",
        )
        c.argument(
            "parameters",
            type=validate_file_or_dict,
            help="Parameters object for the environment. Expected "
            "value: json-string/json-file/@json-file.",
        )
        c.argument("environment_type", type=str, help="Environment type.")
        c.argument("catalog_name", type=str, help="Name of the catalog.")
        c.argument(
            "environment_definition_name",
            options_list=["-e", "--environment-definition-name"],
            type=str,
            help="Name of the environment definition.",
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
            help="The AAD object id of the user. If value is 'me', the identity is taken "
            "from the authentication context.",
        )
        c.argument(
            "environment_name",
            options_list=["--name", "-n", "--environment-name"],
            type=str,
            help="The name " "of the environment.",
        )
        c.argument(
            "parameters",
            type=validate_file_or_dict,
            help="Parameters object for the environment. Expected "
            "value: json-string/json-file/@json-file.",
        )


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
            help="The AAD object id of the user. If value is 'me', the identity is taken from the "
            "authentication context",
        )
        c.argument(
            "environment_name",
            options_list=["--name", "-n", "--environment-name"],
            type=str,
            help="The name " "of the environment.",
        )

    with self.argument_context("devcenter dev catalog list") as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            arg_type=project_type,
        )

    with self.argument_context("devcenter dev catalog show") as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            arg_type=project_type,
        )
        c.argument("catalog_name", type=str, help="The name of the catalog")

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

    with self.argument_context("devcenter dev environment-definition list") as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            required=True,
            arg_type=project_type,
        )
        c.argument("catalog_name", type=str, help="The name of the catalog")

    with self.argument_context("devcenter dev environment-definition show") as c:
        c.argument(
            "dev_center",
            arg_type=dev_center_type,
        )
        c.argument(
            "project_name",
            required=True,
            arg_type=project_type,
        )
        c.argument("catalog_name", type=str, help="The name of the catalog")
        c.argument(
            "definition_name", type=str, help="The name of the environment definition"
        )

    with self.argument_context("devcenter dev artifact list") as c:
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
        c.argument(
            "environment_name",
            options_list=["--name", "-n", "--environment-name"],
            type=str,
            help="The name " "of the environment.",
        )
        c.argument("artifact_path", type=str, help="The path of the artifact.")
