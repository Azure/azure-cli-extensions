# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from argcomplete.completers import FilesCompleter
from azure.cli.core import AzCommandsLoader

from .util.constants import CNF, VNF, BICEP_PUBLISH, ARTIFACT_UPLOAD, IMAGE_UPLOAD


def load_arguments(self: AzCommandsLoader, _):
    from azure.cli.core.commands.parameters import (
        file_type,
        get_enum_type,
        get_three_state_flag,
    )

    definition_type = get_enum_type([VNF, CNF])
    nf_skip_steps = get_enum_type([BICEP_PUBLISH, ARTIFACT_UPLOAD, IMAGE_UPLOAD])
    ns_skip_steps = get_enum_type([BICEP_PUBLISH, ARTIFACT_UPLOAD])

    # Set the argument context so these options are only available when this specific command
    # is called.

    with self.argument_context("aosm nfd") as c:
        c.argument(
            "definition_type",
            arg_type=definition_type,
            help="Type of AOSM definition.",
            required=True,
        )
        c.argument(
            "config_file",
            options_list=["--config-file", "-f"],
            type=file_type,
            completer=FilesCompleter(allowednames="*.json"),
            help="The path to the configuration file.",
        )
        c.argument(
            "clean",
            arg_type=get_three_state_flag(),
            help="Also delete artifact stores, NFD Group and Publisher. Use with care.",
        )
        c.argument(
            "definition_file",
            options_list=["--definition-file", "-b"],
            type=file_type,
            completer=FilesCompleter(allowednames="*.json"),
            help=(
                "Optional path to a bicep file to publish. Use to override publish of"
                " the built definition with an alternative file."
            ),
        )
        c.argument(
            "design_file",
            options_list=["--design-file", "-b"],
            type=file_type,
            completer=FilesCompleter(allowednames="*.bicep"),
            help=(
                "Optional path to a bicep file to publish. Use to override publish of"
                " the built design with an alternative file."
            ),
        )
        c.argument(
            "order_params",
            arg_type=get_three_state_flag(),
            help=(
                "VNF definition_type only - ignored for CNF. Order deploymentParameters"
                " schema and configMappings to have the parameters without default"
                " values at the top and those with default values at the bottom. Can"
                " make it easier to remove those with defaults which you do not want to"
                " expose as NFD parameters."
            ),
        )
        c.argument(
            "interactive",
            options_list=["--interactive", "-i"],
            arg_type=get_three_state_flag(),
            help=(
                "Prompt user to choose every parameter to expose as an NFD parameter."
                " Those without defaults are automatically included."
            ),
        )
        c.argument(
            "parameters_json_file",
            options_list=["--parameters-file", "-p"],
            type=file_type,
            completer=FilesCompleter(allowednames="*.json"),
            help=(
                "Optional path to a parameters file for the bicep definition file. Use"
                " to override publish of the built definition and config with"
                " alternative parameters."
            ),
        )
        c.argument(
            "manifest_file",
            options_list=["--manifest-file", "-m"],
            type=file_type,
            completer=FilesCompleter(allowednames="*.json"),
            help=(
                "Optional path to a bicep file to publish manifests. Use to override"
                " publish of the built definition with an alternative file."
            ),
        )
        c.argument(
            "manifest_params_file",
            options_list=["--manifest-params-file"],
            type=file_type,
            completer=FilesCompleter(allowednames="*.json"),
            help=(
                "Optional path to a parameters file for the manifest definition file."
                " Use to override publish of the built definition and config with"
                " alternative parameters."
            ),
        )
        c.argument(
            "skip",
            arg_type=nf_skip_steps,
            help=(
                "Optional skip steps. 'bicep-publish' will skip deploying the bicep "
                "template; 'artifact-upload' will skip uploading any artifacts; "
                "'image-upload' will skip uploading the VHD image (for VNFs) or the "
                "container images (for CNFs)."
            ),
        )
        c.argument(
            "no_subscription_permissions",
            options_list=["--no-subscription-permissions", "-u"],
            arg_type=get_three_state_flag(),
            help=(
                "CNF definition_type publish only - ignored for VNF."
                " Set to True if you do not "
                "have permission to import to the Publisher subscription (Contributor "
                "role + AcrPush role, or a custom role that allows the importImage "
                "action and AcrPush over the "
                "whole subscription). This means that the image artifacts will be "
                "pulled to your local machine and then pushed to the Artifact Store. "
                "Requires Docker to be installed locally."
            ),
        )

    with self.argument_context("aosm nsd") as c:
        c.argument(
            "config_file",
            options_list=["--config-file", "-f"],
            type=file_type,
            completer=FilesCompleter(allowednames="*.json"),
            help="The path to the configuration file.",
        )
        c.argument("skip", arg_type=ns_skip_steps, help="Optional skip steps")
        c.argument(
            "clean",
            arg_type=get_three_state_flag(),
            help="Also delete NSD Group. Use with care.",
        )
