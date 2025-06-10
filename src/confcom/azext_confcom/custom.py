# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import sys

from pkg_resources import parse_version
from knack.log import get_logger
from azext_confcom.config import (
    DEFAULT_REGO_FRAGMENTS,
    POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS,
    REGO_IMPORT_FILE_STRUCTURE,
)

from azext_confcom import os_util
from azext_confcom.template_util import (
    pretty_print_func,
    print_func,
    str_to_sha256,
    inject_policy_into_template,
    inject_policy_into_yaml,
    print_existing_policy_from_arm_template,
    print_existing_policy_from_yaml,
    get_image_name,
)
from azext_confcom.fragment_util import get_all_fragment_contents
from azext_confcom.init_checks import run_initial_docker_checks
from azext_confcom import security_policy
from azext_confcom.security_policy import OutputType
from azext_confcom.kata_proxy import KataPolicyGenProxy
from azext_confcom.cose_proxy import CoseSignToolProxy
from azext_confcom import oras_proxy


logger = get_logger(__name__)


# pylint: disable=too-many-locals, too-many-branches
def acipolicygen_confcom(
    input_path: str,
    arm_template: str,
    arm_template_parameters: str,
    image_name: str,
    virtual_node_yaml_path: str,
    infrastructure_svn: str,
    tar_mapping_location: str,
    approve_wildcards: str = False,
    outraw: bool = False,
    outraw_pretty_print: bool = False,
    diff: bool = False,
    validate_sidecar: bool = False,
    save_to_file: str = None,
    debug_mode: bool = False,
    print_policy_to_terminal: bool = False,
    disable_stdio: bool = False,
    print_existing_policy: bool = False,
    faster_hashing: bool = False,
    omit_id: bool = False,
    include_fragments: bool = False,
    fragments_json: str = None,
    exclude_default_fragments: bool = False,
):
    if print_existing_policy or outraw or outraw_pretty_print:
        logger.warning(
            "%s %s %s %s %s",
            "Secrets that are included in the provided arm template or configuration files",
            "in the container env or cmd sections will be printed out with this flag.",
            "These are outputed secrets that you must protect. Be sure that you do not include these secrets in your",
            "source control. Also verify that no secrets are present in the logs of your command or script.",
            "For additional information, see http://aka.ms/clisecrets. \n",
        )

    if print_existing_policy and arm_template:
        print_existing_policy_from_arm_template(arm_template, arm_template_parameters)
        return
    if print_existing_policy and virtual_node_yaml_path:
        print_existing_policy_from_yaml(virtual_node_yaml_path)
        return

    if debug_mode:
        logger.warning("WARNING: %s %s",
                       "Debug mode must only be used for debugging purposes. ",
                       "It should not be used for production systems.\n")

    tar_mapping = tar_mapping_validation(tar_mapping_location)

    output_type = get_output_type(outraw, outraw_pretty_print)

    container_group_policies = None

    # warn user that input infrastructure_svn is less than the configured default value
    check_infrastructure_svn(infrastructure_svn)

    fragments_list = []
    # gather information about the fragments being used in the new policy
    if include_fragments:
        fragments_list = os_util.load_json_from_file(fragments_json or input_path)
        if isinstance(fragments_list, dict):
            fragments_list = fragments_list.get("fragments", [])

        # convert to list if it's just a dict
        if not isinstance(fragments_list, list):
            fragments_list = [fragments_list]

    # telling the user what operation we're doing
    logger.warning(
        "Generating security policy for %s: %s in %s",
        "ARM Template" if arm_template else "Image" if image_name else "Input File",
        input_path or arm_template or image_name or virtual_node_yaml_path,
        "base64"
        if output_type == security_policy.OutputType.DEFAULT
        else "clear text",
    )
    # error checking for making sure an input is provided is above
    if input_path:
        container_group_policies = security_policy.load_policy_from_json_file(
            input_path,
            debug_mode=debug_mode,
            infrastructure_svn=infrastructure_svn,
            disable_stdio=disable_stdio,
            exclude_default_fragments=exclude_default_fragments,
        )
    elif arm_template:
        container_group_policies = security_policy.load_policy_from_arm_template_file(
            infrastructure_svn,
            arm_template,
            arm_template_parameters,
            debug_mode=debug_mode,
            disable_stdio=disable_stdio,
            approve_wildcards=approve_wildcards,
            diff_mode=diff,
            rego_imports=fragments_list,
            exclude_default_fragments=exclude_default_fragments,
        )
    elif image_name:
        container_group_policies = security_policy.load_policy_from_image_name(
            image_name, debug_mode=debug_mode, disable_stdio=disable_stdio
        )
    elif virtual_node_yaml_path:
        container_group_policies = security_policy.load_policy_from_virtual_node_yaml_file(
            virtual_node_yaml_path=virtual_node_yaml_path,
            debug_mode=debug_mode,
            disable_stdio=disable_stdio,
            approve_wildcards=approve_wildcards,
            diff_mode=diff,
            rego_imports=fragments_list,
            exclude_default_fragments=exclude_default_fragments,
            infrastructure_svn=infrastructure_svn,
        )

    exit_code = 0

    # standardize the output so we're only operating on arrays
    # this makes more sense than making the "from_file" and "from_image" outputting arrays
    # since they can only ever output a single image's policy
    if not isinstance(container_group_policies, list):
        container_group_policies = [container_group_policies]

    # get all of the fragments that are being used in the policy
    # and associate them with each container group

    if include_fragments:
        logger.info("Including fragments in the policy")
        fragment_policy_list = []
        container_names = []
        fragment_imports = []
        for policy in container_group_policies:
            fragment_imports.extend(policy.get_fragments())
            for container in policy.get_images():
                container_names.append(container.get_container_image())
        # get all the fragments that are being used in the policy
        fragment_policy_list = get_all_fragment_contents(container_names, fragment_imports)
        for policy in container_group_policies:
            policy.set_fragment_contents(fragment_policy_list)

    for count, policy in enumerate(container_group_policies):
        # this is where parameters and variables are populated
        policy.populate_policy_content_for_all_images(
            individual_image=bool(image_name), tar_mapping=tar_mapping, faster_hashing=faster_hashing
        )

        if validate_sidecar:
            exit_code = validate_sidecar_in_policy(policy, output_type == security_policy.OutputType.PRETTY_PRINT)
        elif virtual_node_yaml_path and not (print_policy_to_terminal or outraw or outraw_pretty_print or diff):
            result = inject_policy_into_yaml(
                virtual_node_yaml_path, policy.get_serialized_output(omit_id=omit_id), count
            )
            if result:
                print(str_to_sha256(policy.get_serialized_output(OutputType.RAW, omit_id=omit_id)))
                logger.info("CCE Policy successfully injected into YAML file")
        elif diff:
            exit_code = get_diff_outputs(policy, output_type == security_policy.OutputType.PRETTY_PRINT)
        elif arm_template and not (print_policy_to_terminal or outraw or outraw_pretty_print):
            result = inject_policy_into_template(arm_template, arm_template_parameters,
                                                 policy.get_serialized_output(omit_id=omit_id), count)
            if result:
                # this is always going to be the unencoded policy
                print(str_to_sha256(policy.get_serialized_output(OutputType.RAW, omit_id=omit_id)))
                logger.info("CCE Policy successfully injected into ARM Template")

        else:
            # output to terminal
            print(f"{policy.get_serialized_output(output_type, omit_id=omit_id)}\n\n")

            # output to file
            if save_to_file:
                logger.warning(
                    "%s %s %s",
                    "(Deprecation Warning) the --save-to-file (-s) flag is deprecated ",
                    "and will be removed in a future release. ",
                    "Please print to the console and redirect to a file instead."
                )
                policy.save_to_file(save_to_file, output_type)

    if exit_code != 0:
        sys.exit(exit_code)


# pylint: disable=R0914
def acifragmentgen_confcom(
    image_name: str,
    input_path: str,
    tar_mapping_location: str,
    namespace: str,
    svn: str,
    feed: str,
    key: str,
    chain: str,
    minimum_svn: str,
    image_target: str = "",
    algo: str = "ES384",
    fragment_path: str = None,
    omit_id: bool = False,
    generate_import: bool = False,
    disable_stdio: bool = False,
    debug_mode: bool = False,
    output_filename: str = "",
    outraw: bool = False,
    upload_fragment: bool = False,
    no_print: bool = False,
    fragments_json: str = "",
):
    output_type = get_fragment_output_type(outraw)

    if generate_import:
        cose_client = CoseSignToolProxy()
        import_statements = []
        # images can have multiple fragments attached to them so we need an array to hold the import statements
        if fragment_path:
            import_statements = [cose_client.generate_import_from_path(fragment_path, minimum_svn=minimum_svn)]
        elif image_name:
            import_statements = oras_proxy.generate_imports_from_image_name(image_name, minimum_svn=minimum_svn)

        fragments_file_contents = {}
        fragments_list = []
        if fragments_json:
            logger.info("Creating/appending import statement JSON file")
            if os.path.isfile(fragments_json):
                fragments_file_contents = os_util.load_json_from_file(fragments_json)
                if isinstance(fragments_file_contents, list):
                    logger.error(
                        "%s %s %s %s",
                        "Unsupported JSON file format. ",
                        "Please make sure the outermost structure is not an array. ",
                        "An empty import file should look like: ",
                        REGO_IMPORT_FILE_STRUCTURE
                    )
                    sys.exit(1)
                fragments_list = fragments_file_contents.get(POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS, [])

        # convert to list if it's just a dict
        if isinstance(fragments_list, dict):
            fragments_list = [fragments_list]
        fragments_list += import_statements

        fragments_file_contents[POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS] = fragments_list
        if fragments_json:
            os_util.write_str_to_file(fragments_json, pretty_print_func(fragments_file_contents))
        else:
            print(pretty_print_func(fragments_file_contents))
        return

    tar_mapping = tar_mapping_validation(tar_mapping_location, using_config_file=bool(input_path))

    if image_name:
        policy = security_policy.load_policy_from_image_name(
            image_name, debug_mode=debug_mode, disable_stdio=disable_stdio
        )
    else:
        # this is using --input
        if not tar_mapping:
            tar_mapping = os_util.load_tar_mapping_from_config_file(input_path)
        policy = security_policy.load_policy_from_json_file(
            input_path, debug_mode=debug_mode, disable_stdio=disable_stdio
        )
    # get all of the fragments that are being used in the policy
    # and associate them with each container group
    fragment_policy_list = []
    container_names = []
    fragment_imports = policy.get_fragments()
    for container in policy.get_images():
        container_names.append(container.get_container_image())
    fragment_policy_list = get_all_fragment_contents(container_names, fragment_imports)
    policy.set_fragment_contents(fragment_policy_list)
    policy.populate_policy_content_for_all_images(
        individual_image=bool(image_name), tar_mapping=tar_mapping
    )

    # if no feed is provided, use the first image's feed
    # to assume it's an image-attached fragment
    if not image_target:
        policy_images = policy.get_images()
        if not policy_images:
            logger.error("No images found in the policy or all images are covered by fragments")
            sys.exit(1)
        image_target = policy_images[0].containerImage
    if not feed:
        # strip the tag or hash off the image name so there are stable feed names
        feed = get_image_name(image_target)

    fragment_text = policy.generate_fragment(namespace, svn, output_type, omit_id=omit_id)

    if output_type != security_policy.OutputType.DEFAULT and not no_print:
        print(fragment_text)

    # take ".rego" off the end of the filename if it's there, it'll get added back later
    output_filename = output_filename.replace(".rego", "")
    filename = f"{output_filename or namespace}.rego"
    os_util.write_str_to_file(filename, fragment_text)

    if key:
        cose_proxy = CoseSignToolProxy()
        iss = cose_proxy.create_issuer(chain)
        out_path = filename + ".cose"

        cose_proxy.cose_sign(filename, key, chain, feed, iss, algo, out_path)
        if upload_fragment:
            oras_proxy.attach_fragment_to_image(image_target, out_path)


def katapolicygen_confcom(
    yaml_path: str,
    config_map_file: str,
    outraw: bool = False,
    print_policy: bool = False,
    use_cached_files: bool = False,
    settings_file_name: str = None,
    rules_file_name: str = None,
    print_version: bool = False,
    containerd_pull: str = False,
    containerd_socket_path: str = None,
):
    kata_proxy = KataPolicyGenProxy()

    output = kata_proxy.kata_genpolicy(
        yaml_path,
        config_map_file=config_map_file,
        outraw=outraw,
        print_policy=print_policy,
        use_cached_files=use_cached_files,
        settings_file_name=settings_file_name,
        rules_file_name=rules_file_name,
        print_version=print_version,
        containerd_pull=containerd_pull,
        containerd_socket_path=containerd_socket_path,
    )
    print(output)


def update_confcom(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param("tags", tags)
    return instance


def check_infrastructure_svn(infrastructure_svn):
    if infrastructure_svn and parse_version(infrastructure_svn) < parse_version(
        DEFAULT_REGO_FRAGMENTS[0]["minimum_svn"]
    ):
        logger.warning(
            "Input Infrastructure Fragment Software Version Number is less than the default Infrastructure SVN: %s",
            DEFAULT_REGO_FRAGMENTS[0]["minimum_svn"],
        )


def validate_sidecar_in_policy(policy: security_policy.AciPolicy, outraw_pretty_print: bool):
    is_valid, output = policy.validate_sidecars()

    if outraw_pretty_print:
        formatted_output = pretty_print_func(output)
    else:
        formatted_output = print_func(output)

    if is_valid:
        print("Sidecar containers will pass with its generated policy")
        return 0

    print(
        f"Sidecar containers will not pass with its generated policy: {formatted_output}"
    )
    return 2


def get_diff_outputs(policy: security_policy.AciPolicy, outraw_pretty_print: bool):
    exit_code = 0
    is_valid, output = policy.validate_cce_policy()

    if outraw_pretty_print:
        formatted_output = pretty_print_func(output)
    else:
        formatted_output = print_func(output)

    print(
        "Existing policy and Template match"
        if is_valid
        else formatted_output
    )
    fragment_diff = policy.compare_fragments()

    if fragment_diff != {}:
        logger.warning(
            "Fragments in the existing policy are not the defaults. If this is expected, ignore this warning."
        )
    if not is_valid:
        logger.warning(
            "Existing Policy and Template differ. Consider recreating the base64-encoded policy."
        )
        exit_code = 2
    return exit_code


# TODO: refactor this function to use _validators.py functions and make sure the tar path
# isn't coming from the config file rather than the flag
def tar_mapping_validation(tar_mapping_location: str, using_config_file: bool = False):
    tar_mapping = None
    if tar_mapping_location:
        if not os.path.isfile(tar_mapping_location):
            print(
                "--tar input must either be a path to a json file with "
                + "image to tar location mappings or the location to a single tar file."
            )
            sys.exit(2)
        # file is mapping images to tar file locations
        elif tar_mapping_location.endswith(".json"):
            tar_mapping = os_util.load_tar_mapping_from_file(tar_mapping_location)
        # passing in a single tar location for a single image policy
        else:
            tar_mapping = tar_mapping_location
    elif not using_config_file:
        # only need to do the docker checks if we're not grabbing image info from tar files
        error_msg = run_initial_docker_checks()
        if error_msg:
            logger.warning(error_msg)
            sys.exit(1)
    return tar_mapping


def get_output_type(outraw, outraw_pretty_print):
    output_type = security_policy.OutputType.DEFAULT
    if outraw:
        output_type = security_policy.OutputType.RAW
    elif outraw_pretty_print:
        output_type = security_policy.OutputType.PRETTY_PRINT
    return output_type


def get_fragment_output_type(outraw):
    output_type = security_policy.OutputType.PRETTY_PRINT
    if outraw:
        output_type = security_policy.OutputType.RAW
    return output_type
