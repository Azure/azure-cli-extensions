# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from knack.log import get_logger
from azext_confcom.config import RESERVED_FRAGMENT_NAMES, SUPPORTED_ALGOS


logger = get_logger(__name__)


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


def validate_infrastructure_svn(namespace):
    if namespace.infrastructure_svn and namespace.exclude_default_fragments:
        raise CLIError("Cannot set infrastructure SVN without using default fragments")


def validate_aci_source(namespace):
    if sum(map(bool, [
        namespace.input_path,
        namespace.arm_template,
        namespace.image_name,
        namespace.virtual_node_yaml_path,
        namespace.container_definitions is not None,
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


def validate_fragment_json_policy(namespace):
    if namespace.fragments_json and not namespace.include_fragments:
        raise CLIError("Must provide --include-fragments to reference a fragment import JSON file")


def validate_katapolicygen_input(namespace):
    if not (namespace.yaml_path or namespace.print_version):
        raise CLIError("Either --yaml-path or --print-version is required")


def validate_fragment_key_and_chain(namespace):
    if sum(map(bool, [namespace.key, namespace.chain])) == 1:
        raise CLIError("Must provide both --key and --chain to sign a fragment")


def validate_fragment_source(namespace):
    if not namespace.generate_import and sum(map(bool, [
        namespace.image_name,
        namespace.input_path,
        namespace.container_definitions is not None,
    ])) != 1:
        raise CLIError("Must provide either an image name or an input file to generate a fragment")


def validate_image_target(namespace):
    if namespace.image_target and not namespace.upload_fragment:
        raise CLIError("Must specify --upload-fragment to use --image-target")


def validate_upload_fragment(namespace):
    if namespace.upload_fragment and not (namespace.key or namespace.chain):
        raise CLIError("Must sign the fragment with --key and --chain to upload it")
    if namespace.upload_fragment and not (namespace.image_target or namespace.feed):
        raise CLIError("Must either specify an --image-target or --feed to upload a fragment")


def validate_fragment_generate_import(namespace):
    if namespace.generate_import and sum(map(bool, [
        namespace.fragment_path,
        namespace.image_name
    ])) != 1:
        raise CLIError(
            (
                "Must provide either a fragment path or "
                "an image name to generate an import statement"
            )
        )
    if namespace.generate_import and namespace.output_filename:
        raise CLIError(
            "Cannot specify an output file (--output-filename) when generating an import statement." +
            "Use --fragments-json (-j) to write to a file."
        )


def validate_fragment_namespace_and_svn(namespace):
    if not namespace.generate_import and (not namespace.namespace or not namespace.svn):
        raise CLIError("Must provide both --namespace and --svn to generate a fragment")
    if not namespace.generate_import and namespace.namespace in RESERVED_FRAGMENT_NAMES:
        raise CLIError(f"Namespace '{namespace.namespace}' is reserved")
    if namespace.svn and not namespace.svn.isdigit():
        raise CLIError("--svn must be an integer")
    if not namespace.generate_import and (namespace.svn and int(namespace.svn) < 0):
        raise CLIError("--svn must be greater than or equal to 0")


def validate_fragment_minimum_svn(namespace):
    if namespace.generate_import and (not namespace.minimum_svn or int(namespace.minimum_svn) < 0):
        raise CLIError("--minimum-svn must be greater than or equal to 0")


def validate_fragment_algo(namespace):
    validate_fragment_key_and_chain(namespace)
    if namespace.algo not in SUPPORTED_ALGOS:
        raise CLIError(f"Algorithm '{namespace.algo}' is not supported. Supported algorithms are {SUPPORTED_ALGOS}")


def validate_fragment_path(namespace):
    if namespace.fragment_path and not namespace.generate_import:
        raise CLIError("Must provide --generate-import to specify a fragment path")


def validate_fragment_json(namespace):
    if namespace.fragments_json and not namespace.generate_import:
        raise CLIError("Must provide --fragment-path to place a fragment import into a file")


def validate_stdio(namespace):
    if namespace.enable_stdio and namespace.disable_stdio:
        raise CLIError('Use only one of --enable-stdio or --disable-stdio.')


def resolve_stdio(enable_stdio_flag, disable_stdio_flag, default=True):

    stdio_enabled = default
    if enable_stdio_flag is None and disable_stdio_flag is None:
        logger.warning(
            "WARNING: Using default stdio setting (Enabled)\n"
            "For the most secure deployments, ensure stdio is disabled. "
            "Default behaviour may change in the future, you can set stdio with:\n"
            "    --disable-stdio\n"
            "    --enable-stdio\n"
        )
    elif enable_stdio_flag is not None:
        stdio_enabled = enable_stdio_flag
    elif disable_stdio_flag is not None:
        stdio_enabled = not disable_stdio_flag

    return stdio_enabled
