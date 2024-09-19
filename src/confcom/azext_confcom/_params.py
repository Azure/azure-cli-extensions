# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType
from azext_confcom._validators import (
    validate_params_file,
    validate_diff,
    validate_aci_source,
    validate_print_format,
    validate_save_to_file,
    validate_faster_hashing,
    validate_katapolicygen_input,
)


def load_arguments(self, _):

    from azure.cli.core.commands.parameters import tags_type

    confcom_name_type = CLIArgumentType(
        options_list="--confcom-name-name",
        help="Name of the Confidential Container Security Policy Generator.",
        id_part="name",
    )

    with self.argument_context("confcom") as c:
        c.argument("tags", tags_type)
        c.argument("confcom_name", confcom_name_type, options_list=["--name", "-n"])

    with self.argument_context("confcom acipolicygen") as c:
        c.argument(
            "input_path",
            options_list=("--input", "-i"),
            required=False,
            help="Input JSON config file",
            validator=validate_aci_source
        )
        c.argument(
            "arm_template",
            options_list=("--template-file", "-a"),
            required=False,
            help="ARM template file",
            validator=validate_aci_source
        )
        c.argument(
            "arm_template_parameters",
            options_list=("--parameters", "-p"),
            required=False,
            help="ARM template parameters",
            validator=validate_params_file
        )
        c.argument(
            "virtual_node_yaml_path",
            options_list=("--virtual-node-yaml"),
            required=False,
            help="Virtual node YAML file",
            validator=validate_aci_source
        )
        c.argument(
            "image_name",
            options_list=("--image",),
            required=False,
            help="Image Name",
            validator=validate_aci_source
        )
        c.argument(
            "tar_mapping_location",
            options_list=("--tar",),
            required=False,
            help="Tar File locations in JSON format where the key is the name and tag of the image and the value is the path to the tar file",
        )
        c.argument(
            "infrastructure_svn",
            options_list=("--infrastructure-svn",),
            required=False,
            help="Minimum Allowed Software Version Number for Infrastructure Fragment",
        )
        c.argument(
            "debug_mode",
            options_list=("--debug-mode",),
            required=False,
            help="Debug mode will enable processes in a container group that are helpful for debugging",
        )
        c.argument(
            "approve_wildcards",
            options_list=("--approve-wildcards", "-y"),
            required=False,
            help="Approving wildcards by default will get rid of the prompts during the wildcard environment variable use case and auto-approve the use of wildcards",
        )
        c.argument(
            "disable_stdio",
            options_list=("--disable-stdio",),
            required=False,
            help="Disabling container stdio will disable the ability to see the output of the container in the terminal for Confidential ACI",
        )
        c.argument(
            "diff",
            options_list=("--diff", "-d"),
            required=False,
            help="Compare the CCE Policy field in the ARM Template to the containers in the ARM Template and make sure they are compatible",
            validator=validate_diff
        )
        c.argument(
            "validate_sidecar",
            options_list=("--validate-sidecar", "-v"),
            required=False,
            help="Validate that the image used to generate the CCE Policy for a sidecar container will be allowed by its generated policy",
        )
        c.argument(
            "print_existing_policy",
            options_list=("--print-existing-policy"),
            required=False,
            action="store_true",
            help="Pretty print the existing policy in the ARM Template",
        )
        c.argument(
            "outraw",
            options_list=("--outraw"),
            required=False,
            action="store_true",
            help="Output policy in clear text compact JSON instead of default base64 format",
            validator=validate_print_format,
        )
        c.argument(
            "outraw_pretty_print",
            options_list=("--outraw-pretty-print"),
            required=False,
            action="store_true",
            help="Output policy in clear text and pretty print format",
            validator=validate_print_format,
        )
        c.argument(
            "save_to_file",
            options_list=("--save-to-file", "-s"),
            required=False,
            help="Save output policy to given file path",
            validator=validate_save_to_file,
        )
        c.argument(
            "print_policy_to_terminal",
            options_list=("--print-policy"),
            required=False,
            help="Print the generated policy in the terminal",
            validator=validate_print_format,
        )
        c.argument(
            "faster_hashing",
            options_list=("--faster-hashing"),
            required=False,
            help="Use buffered image reader for dmverity hashing. This will speed up the hashing process but use much more memory.",
            validator=validate_faster_hashing,
        )

    with self.argument_context("confcom katapolicygen") as c:
        c.argument(
            "yaml_path",
            options_list=("--yaml", "-y"),
            required=False,
            help="Input YAML config file",
            validator=validate_katapolicygen_input,
        )
        c.argument(
            "outraw",
            options_list=("--outraw"),
            required=False,
            help="Print the generated policy in the terminal in Rego format",
            validator=validate_katapolicygen_input,
        )
        c.argument(
            "print_policy",
            options_list=("--print-policy"),
            required=False,
            help="Print the generated policy in the terminal in base64",
            validator=validate_katapolicygen_input,
        )
        c.argument(
            "config_map_file",
            options_list=("--config-map-file", "-c"),
            required=False,
            help="Config map file",
            validator=validate_katapolicygen_input,
        )
        c.argument(
            "use_cached_files",
            options_list=("--use-cached-files", "-u"),
            required=False,
            help="Use cached files",
            validator=validate_katapolicygen_input,
        )
        c.argument(
            "settings_file_name",
            options_list=("--settings-file-name", "-j"),
            required=False,
            help="Path for custom settings file",
            validator=validate_katapolicygen_input,
        )
        c.argument(
            "rules_file_name",
            options_list=("--rules-file-name", "-p"),
            required=False,
            help="Path for custom rules file",
            validator=validate_katapolicygen_input,
        )
        c.argument(
            "print_version",
            options_list=("--print-version", "-v"),
            required=False,
            help="Print the version of the genpolicy tool",
            validator=validate_katapolicygen_input,
        )
        c.argument(
            "containerd_pull",
            options_list=("--containerd-pull", "-d"),
            required=False,
            help="Use containerd to pull the image",
            validator=validate_katapolicygen_input,
        )
        c.argument(
            "containerd_socket_path",
            options_list=("--containerd-socket-path"),
            required=False,
            help="Path to containerd socket if not using the default",
            validator=validate_katapolicygen_input,
        )
