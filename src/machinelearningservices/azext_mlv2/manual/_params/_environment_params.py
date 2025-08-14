# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml.constants._common import YAMLRefDocLinks

from ._common_params import (
    add_archived_only_param,
    add_common_params,
    add_datastore_param,
    add_description_param,
    add_file_param,
    add_include_archived_param,
    add_max_results_params,
    add_override_param,
    add_registry_param,
    add_tags_param,
)


def add_version_param(c):
    c.argument("version", options_list=["--version", "-v"], type=str, help="Version of the environment.")


def add_name_param(c):
    c.argument("name", options_list=["--name", "-n"], type=str, help="Name of the environment.")


def add_label_param(c):
    c.argument("label", options_list=["--label", "-l"], help="Label of the environment.")


def load_environment_params(self):
    with self.argument_context("ml environment create") as c:
        add_common_params(c)
        add_name_param(c)
        add_registry_param(c)
        add_file_param(c, "environment", YAMLRefDocLinks.ENVIRONMENT)
        add_override_param(c)
        add_version_param(c)
        add_tags_param(c)
        add_description_param(c, help_message="Description of the environment.")
        add_datastore_param(c)
        c.argument(
            "image",
            options_list=["--image", "-i"],
            help="Docker image. --image/-i and --build-context/-b are mutually exclusive arguments.",
        )
        c.argument(
            "conda_file",
            options_list=["--conda-file", "-c"],
            help="Local path to a conda specification file. --image/-i must also be specified if "
                 "this argument is used.",
        )
        c.argument(
            "build_context",
            options_list=["--build-context", "-b"],
            help="Local path to the directory to use as a Docker build context. --build-context/-b and "
                 "--image/-i are mutually exclusive arguments.",
        )
        c.argument(
            "dockerfile_path",
            options_list=["--dockerfile-path", "-d"],
            help="Relative path to the Dockerfile within the directory specified by --build-context/-b. "
                 "If omitted, './Dockerfile' is used.",
        )
        c.argument(
            "os_type",
            options_list=["--os-type"],
            help="Type of operating system. Allowed values: linux, windows. Default: linux.",
        )
        c.argument(
            "path",
            options_list=["--path", "-p"],
            help="Path of the environment asset in the workspace that will be copied to the registry, "
                 "only applicable with --registry-name parameter, else it will be ignored.",
        )

    with self.argument_context("ml environment show") as c:
        add_common_params(c)
        add_registry_param(c)
        c.argument(
            "version",
            options_list=["--version", "-v"],
            help="Version of the environment.",
        )
        add_version_param(c)
        add_name_param(c)
        add_label_param(c)

    with self.argument_context("ml environment list") as c:
        add_common_params(c)
        add_registry_param(c)
        c.argument(
            "name",
            options_list=["--name", "-n"],
            help="Name of the environment. If provided, all the environment versions under this name will be returned.",
        )
        add_max_results_params(c)
        add_include_archived_param(c, help_message="List archived environments and active environments.")
        add_archived_only_param(c, help_message="List archived environments only.")

    with self.argument_context("ml environment update") as c:
        add_common_params(c)
        add_registry_param(c)
        add_version_param(c)
        add_name_param(c)
        add_description_param(c, help_message="Description of the environment.")
        add_label_param(c)

    with self.argument_context("ml environment archive") as c:
        add_common_params(c)
        add_version_param(c)
        add_name_param(c)
        add_label_param(c)
        add_registry_param(c)

    with self.argument_context("ml environment restore") as c:
        add_common_params(c)
        add_version_param(c)
        add_name_param(c)
        add_label_param(c)
        add_registry_param(c)

    with self.argument_context("ml environment share") as c:
        add_common_params(c)
        add_name_param(c)
        add_version_param(c)
        add_registry_param(c)
        c.argument("share_with_name", help="Name  of the environment to be created with.")
        c.argument("share_with_version", help="Version  of the environment to be created with.")
        c.argument("registry_name", help="Destination registry.")
