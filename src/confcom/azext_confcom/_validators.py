# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError


def validate_params_file(namespace):
    if namespace.arm_template_parameters and not namespace.arm_template:
        raise CLIError(
            "Can only use ARM Template Parameters if ARM Template is also present"
        )


def validate_diff(namespace):
    if (namespace.diff and namespace.input_path) or (namespace.diff and namespace.image_name):
        raise CLIError("Can only diff CCE policy from ARM Template or YAML File")


def validate_print_format(namespace):
    if sum(map(bool, [namespace.print_policy_to_terminal, namespace.outraw, namespace.outraw_pretty_print])) > 1:
        raise CLIError("Can only print in one format at a time")


def validate_aci_source(namespace):
    if sum(map(bool, [
        namespace.input_path,
        namespace.arm_template,
        namespace.image_name,
        namespace.virtual_node_yaml_path
    ])) != 1:
        raise CLIError("Can only generate CCE policy from one source at a time")


def validate_faster_hashing(namespace):
    if namespace.faster_hashing and namespace.tar_mapping_location:
        raise CLIError("Cannot use --faster-hashing with --tar")


def validate_save_to_file(namespace):
    if namespace.save_to_file and namespace.arm_template and not (
        namespace.print_policy_to_terminal or namespace.outraw or namespace.outraw_pretty_print
    ):
        raise CLIError("Must print policy to terminal when saving to file")


def validate_katapolicygen_input(namespace):
    if namespace.yaml_path and not namespace.print_version:
        raise CLIError("Either --yaml-path or --print-version is required")
