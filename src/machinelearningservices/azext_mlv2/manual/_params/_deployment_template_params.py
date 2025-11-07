# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from ._common_params import (
    add_common_params,
    add_description_param,
    add_file_param,
    add_lro_param,
    add_override_param,
    add_tags_param,
)


def add_deployment_template_common_param(
    c,
    name_help_message="Name of the deployment template.",
    version_help_message="Version of the deployment template.",
    name_required=True,
    version_required=True,
):
    c.argument("name", options_list=["--name", "-n"], help=name_help_message, required=name_required)
    c.argument("version", options_list=["--version", "-v"], help=version_help_message, required=version_required)


def load_deployment_template_params(self):
    with self.argument_context("ml deployment-template list") as c:
        add_common_params(c)
        c.argument(
            "registry_name",
            options_list=["--registry-name", "-r"],
            required=True,
            help=(
                "Name of the registry. This is required since deployment templates "
                "only support registry-name and not workspace."
            ),
        )

    with self.argument_context("ml deployment-template show") as c:
        add_common_params(c)
        add_deployment_template_common_param(c, name_required=True, version_required=True)
        c.argument(
            "registry_name",
            options_list=["--registry-name", "-r"],
            required=True,
            help=(
                "Name of the registry. This is required since deployment templates "
                "only support registry-name and not workspace."
            ),
        )

    with self.argument_context("ml deployment-template create") as c:
        add_common_params(c)
        # Optional for create since they can come from file
        add_deployment_template_common_param(c, name_required=False, version_required=False)
        add_lro_param(c)
        add_file_param(c, "deployment-template", "https://aka.ms/ml-cli-v2-deployment-template-yaml")
        add_override_param(c)
        c.argument(
            "registry_name",
            options_list=["--registry-name", "-r"],
            required=True,
            help=(
                "Name of the registry. This is required since deployment templates "
                "only support registry-name and not workspace."
            ),
        )

    with self.argument_context("ml deployment-template update") as c:
        add_common_params(c)
        add_deployment_template_common_param(c, name_required=True, version_required=True)
        add_override_param(c)
        add_description_param(c, help_message="Description of the deployment template.")
        add_tags_param(c)
        c.argument(
            "registry_name",
            options_list=["--registry-name", "-r"],
            required=True,
            help=(
                "Name of the registry. This is required since deployment templates "
                "only support registry-name and not workspace."
            ),
        )

    with self.argument_context("ml deployment-template archive") as c:
        add_common_params(c)
        add_deployment_template_common_param(c, name_required=True, version_required=True)
        add_lro_param(c)
        c.argument(
            "registry_name",
            options_list=["--registry-name", "-r"],
            required=True,
            help=(
                "Name of the registry. This is required since deployment templates "
                "only support registry-name and not workspace."
            ),
        )

    with self.argument_context("ml deployment-template restore") as c:
        add_common_params(c)
        add_deployment_template_common_param(c, name_required=True, version_required=True)
        add_lro_param(c)
        c.argument(
            "registry_name",
            options_list=["--registry-name", "-r"],
            required=True,
            help=(
                "Name of the registry. This is required since deployment templates "
                "only support registry-name and not workspace."
            ),
        )
