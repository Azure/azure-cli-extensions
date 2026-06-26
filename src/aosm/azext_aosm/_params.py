# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from argcomplete.completers import FilesCompleter
from azure.cli.core import AzCommandsLoader

from .common.constants import (
    CNF,
    VNF,
    VNF_NEXUS,
    BICEP_PUBLISH,
    ARTIFACT_UPLOAD,
    HELM_TEMPLATE,
    IMAGE_UPLOAD,
)


def load_arguments(self: AzCommandsLoader, _):
    from azure.cli.core.commands.parameters import (
        file_type,
        get_enum_type,
        get_three_state_flag,
    )

    definition_type = get_enum_type([VNF, CNF, VNF_NEXUS])
    nf_skip_steps = get_enum_type(
        [BICEP_PUBLISH, ARTIFACT_UPLOAD, IMAGE_UPLOAD, HELM_TEMPLATE]
    )

    # Set the argument context so these options are only available when this specific command
    # is called.
    with self.argument_context("aosm nfd") as c:
        c.argument(
            "definition_type",
            arg_type=definition_type,
            help=(
                "Type of AOSM definition to be published. The config file differs"
                " depending on type."
            ),
            required=True,
        )
        c.argument(
            "output_file",
            options_list=["--output-file"],
            help="The name of the output file to write the generated config text to.",
            required=False,
        )
        c.argument(
            "config_file",
            options_list=["--config-file", "-f"],
            type=file_type,
            completer=FilesCompleter(allowednames="*.jsonc"),
            help=(
                "The path to the configuration file. This is a JSONC file that contains"
                " the required parameters for building the NFD."
            ),
        )
        c.argument(
            "clean",
            arg_type=get_three_state_flag(),
            help="Also delete artifact stores, NFD Group and Publisher. Use with care.",
        )
        c.argument(
            "build_output_folder",
            options_list=["--build-output-folder", "-b"],
            type=file_type,
            completer=FilesCompleter(allowednames="*.json"),
            help="Path to the folder to publish, created by the build command.",
        )
        # This will only ever output one string and will fail if more than one
        # skip steps are provided. It might be good to change that.
        c.argument(
            "skip",
            arg_type=nf_skip_steps,
            help=(
                "Optional skip step. Providing the string 'helm-template' will skip "
                "templating the helm charts (for CNFs), but is very likely to result in "
                "a broken deployment as image versions will not be parsed. Intended only for "
                "temporarily unblocking during development."
            ),
        )
        c.argument(
            "no_subscription_permissions",
            options_list=["--no-subscription-permissions", "-u"],
            arg_type=get_three_state_flag(),
            help=(
                "Used only for CNF publish - ignored in all other scenarios. Pass this"
                " flag if you do not have permission to import to the Publisher"
                " subscription (Contributor role + AcrPush role, or a custom role that"
                " allows the importImage action and AcrPush over the whole"
                " subscription). Using this flag causes image artifacts to be pulled to"
                " your local machine and then pushed to the Artifact Store. This is"
                " slower than a copy entirely within Azure, but is an alternative if"
                " you do not have the required permissions. Requires Docker to be"
                " installed locally."
            ),
        )

    with self.argument_context("aosm nsd") as c:
        c.argument(
            "output_file",
            options_list=["--output-file"],
            help="The name of the output file to write the generated config text to.",
            required=False,
        )
        c.argument(
            "config_file",
            options_list=["--config-file", "-f"],
            type=file_type,
            completer=FilesCompleter(allowednames="*.jsonc"),
            help=(
                "The path to the configuration file. This is a JSONC file that contains"
                " the required parameters for building the NSD."
            ),
        )
        # NSD skip steps are not currently implemented. This is a record of how to add them.
        # You also need to add the `skip` parameter in the relevant function in custom.py.
        # c.argument("skip", arg_type=ns_skip_steps, help="Optional skip steps")
        c.argument(
            "clean",
            arg_type=get_three_state_flag(),
            help="Also delete NSD Group. Use with care.",
        )
        c.argument(
            "build_output_folder",
            options_list=["--build-output-folder", "-b"],
            type=file_type,
            completer=FilesCompleter(allowednames="*.json"),
            help="Path to the folder to publish, created by the build command.",
        )
        c.argument(
            "no_subscription_permissions",
            options_list=["--no-subscription-permissions", "-u"],
            completer=FilesCompleter(allowednames="*.json"),
            help=(
                "CNF definition_type publish only - ignored for VNF. "
                "Pass this flag if you do not have permission to import to the "
                "Publisher subscription (Contributor role + AcrPush role, or a "
                "custom role that allows the importImage action and AcrPush over the "
                "whole subscription). This means that the image artifacts will be "
                "pulled to your local machine and then pushed to the Artifact Store. "
                "Requires Docker to be installed locally."
            ),
        )

    with self.argument_context("aosm sns") as c:
        c.argument(
            "output_file",
            options_list=["--output-file"],
            help="The name of the output file to write the generated config text to.",
            required=False,
        )
        c.argument(
            "config_file",
            options_list=["--config-file", "-f"],
            type=file_type,
            completer=FilesCompleter(allowednames="*.jsonc"),
            help=(
                "The path to the configuration file. This is a JSONC file that contains"
                " the required parameters for building the NSD."
            ),
        )
        c.argument(
            "build_output_folder",
            options_list=["--build-output-folder", "-b"],
            type=file_type,
            completer=FilesCompleter(allowednames="*.json"),
            help="Path to the folder to deploy, created by the build command.",
        )
        c.argument(
            "no_subscription_permissions",
            options_list=["--no-subscription-permissions", "-u"],
            completer=FilesCompleter(allowednames="*.json"),
            help=(
                "Pass this flag if you do not have permission to import to the "
                "Publisher subscription (Contributor role + AcrPush role, or a "
                "custom role that allows the importImage action and AcrPush over the "
                "whole subscription). This means that the image artifacts will be "
                "pulled to your local machine and then pushed to the Artifact Store. "
                "Requires Docker to be installed locally."
            ),
        )
