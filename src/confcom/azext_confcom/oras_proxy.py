# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import platform
import re
import subprocess
from tempfile import mkdtemp
from typing import List

from azext_confcom.config import ARTIFACT_TYPE, DEFAULT_REGO_FRAGMENTS
from azext_confcom.cose_proxy import CoseSignToolProxy
from azext_confcom.errors import eprint
from azext_confcom.os_util import clean_up_temp_folder, delete_silently
from azext_confcom.template_util import (
    extract_containers_and_fragments_from_text, extract_svn_from_text)
from knack.log import get_logger

host_os = platform.system()
machine = platform.machine()
SHA256_PREFIX = "@sha256:"

logger = get_logger(__name__)


def prepend_docker_registry(image_name: str) -> str:
    """
    Normalize a Docker image reference by adding `docker.io/library` if necessary.

    Args:
        image (str): The Docker image reference (e.g., `nginx:latest` or `myrepo/myimage`).

    Returns:
        str: The normalized Docker image reference.
    """
    # Split the image into name and tag
    if ":" in image_name:
        name, _ = image_name.rsplit(":", 1)
    else:
        name, _ = image_name, "latest"

    registry = ""
    # Check if the image name contains a registry (e.g., docker.io, custom registry)
    if ("/" not in name or "." not in name.split("/")[0]) and not name.startswith("localhost"):
        # If no registry is specified, assume docker.io/library
        if "/" not in name:
            # Add the `library` namespace for official images
            registry = "library/"
        # Add the default `docker.io` registry
        registry = f"docker.io/{registry}"

    return f"{registry}{image_name}"


def call_oras_cli(args, check=False):
    return subprocess.run(args, check=check, capture_output=True, timeout=120)


# discover if there are policy artifacts associated with the image
# return their digests in a list if there are some
def discover(
    image: str,
) -> tuple[bool, List[str]]:
    image_exists = True
    # normalize the name in case the docker registry is implied
    image = prepend_docker_registry(image)

    arg_list = ["oras", "discover", image, "-o", "json", "--artifact-type", ARTIFACT_TYPE]
    item = call_oras_cli(arg_list, check=False)
    hashes = []

    logger.info("Discovering fragments for %s: %s", image, item.stdout.decode('utf-8'))
    if item.returncode == 0:
        json_output = json.loads(item.stdout.decode("utf-8"))
        manifests = json_output.get("manifests", [])
        if manifests is not None:
            for manifest in manifests:
                hashes.append(manifest["digest"])
    # get the exit code from the subprocess
    else:
        err_str = item.stderr.decode("utf-8")
        if "unauthorized" in err_str.lower():
            logger.warning(
                "Error pulling the policy fragment from %s.\n\nPlease log into the registry and try again.\n\n",
                image
            )
            image_exists = False
        # this happens when the image isn't found in the remote repo or there is no access to the remote repo
        elif f"{image}: not found" in err_str:
            logger.warning("No policy fragments found for image %s", image)
            image_exists = False
        elif "dial tcp: lookup" in err_str:
            logger.warning("Could not access registry for %s", image)
            image_exists = False
        else:
            eprint(f"Error retrieving fragments from remote repo: {err_str}", exit_code=item.returncode)
    return image_exists, hashes


def pull(
    artifact: str,
    hash_val: str = "",
    tag: str = "",
) -> str:
    """
    pull the policy fragment from the remote repo and return its filepath after downloaded.
    This file must be cleaned up after use.
    """

    full_path = ""
    if SHA256_PREFIX in artifact:
        artifact, temp_hash_val = artifact.split(SHA256_PREFIX)
        if temp_hash_val != hash_val:
            eprint(f"Input '{hash_val}' does not match what is present in registry '{temp_hash_val}'")
        full_path = f"{artifact}{SHA256_PREFIX}{hash_val}"
    elif artifact and hash_val:
        # response from discover function includes "sha256:" but not "@"
        full_path = f"{artifact}@{hash_val}"
    elif ":" in artifact:
        artifact, tag = artifact.rsplit(":", maxsplit=1)
        full_path = f"{artifact}:{tag}"
    else:
        eprint(f"Invalid artifact name: {artifact}")
    logger.info("Pulling fragment: %s", full_path)

    temp_folder = mkdtemp()
    arg_list = ["oras", "pull", full_path, "-o", temp_folder]

    item = call_oras_cli(arg_list, check=False)

    # get the exit code from the subprocess
    if item.returncode != 0:
        if "401: Unauthorized" in item.stderr.decode("utf-8"):
            eprint(
                f"Error pulling the policy fragment: {full_path}.\n\n"
                + "Please log into the registry and try again.\n\n"
            )
        eprint(f"Error while pulling fragment: {item.stderr.decode('utf-8')}", exit_code=item.returncode)

    # extract the file name from stdout
    filename = ""
    lines = item.stdout.decode("utf-8").splitlines()
    for line in lines:
        if "Downloaded" in line:
            filename = line.split(" ")[-1]
            break

    if filename == "":
        eprint(f"Could not find the filename of the pulled fragment for {full_path}")
    out_filename = os.path.join(temp_folder, filename)
    return out_filename


def pull_all_image_attached_fragments(image):
    # TODO: be smart about if we're pulling a fragment directly or trying to discover them from an image tag
    # TODO: this will be for standalone fragments
    image_exists, fragments = discover(image)
    fragment_contents = []
    feeds = []
    if image_exists:
        proxy = CoseSignToolProxy()
        for fragment_digest in fragments:
            filename = pull(image, hash_val=fragment_digest)
            text = proxy.extract_payload_from_path(filename)
            feed = proxy.extract_feed_from_path(filename)
            clean_up_temp_folder(filename)
            fragment_contents.append(text)
            feeds.append(feed)

    return fragment_contents, feeds


def create_list_of_standalone_imports(fragment_feeds):
    # the output will be a list of dicts that will reflect the same output as pull_all_standalone_fragments
    proxy = CoseSignToolProxy()
    standalone_imports = []
    for feed in fragment_feeds:
        filename = pull(artifact=feed)
        standalone_import = proxy.generate_import_from_path(filename, minimum_svn=-1)
        clean_up_temp_folder(filename)
        standalone_imports.append(standalone_import)
    return standalone_imports


def pull_all_standalone_fragments(fragment_imports):
    fragment_contents = []
    feeds = []
    proxy = CoseSignToolProxy()

    for fragment in fragment_imports:
        if fragment in DEFAULT_REGO_FRAGMENTS:
            continue
        path = fragment.get("path")
        feed = fragment.get("feed")
        minimum_svn = int(fragment.get("minimum_svn"))
        feeds.append(feed)

        if path:
            text = proxy.extract_payload_from_path(path)
        else:
            filename = pull(artifact=feed)
            text = proxy.extract_payload_from_path(filename)
            svn = extract_svn_from_text(text)
            if svn < minimum_svn:
                logger.warning(
                    "found fragment %s but the svn of %s is lower than the the specified minimum_svn of %s",
                    feed,
                    svn,
                    minimum_svn
                )
                continue
            clean_up_temp_folder(filename)
        # put new fragments to the end of the list
        fragment_contents.append(text)
        _, fragments = extract_containers_and_fragments_from_text(text)
        fragment_imports.extend(fragments)

    return fragment_contents, feeds


def check_oras_cli():
    text = "ORAS CLI not installed. Please install ORAS CLI: https://oras.land/docs/installation"
    try:
        item = call_oras_cli(["oras", "version"], check=False)
        if item.returncode != 0:
            eprint(text)
    except FileNotFoundError:
        eprint(text)


# used for image-attached fragments
def attach_fragment_to_image(image_name: str, filename: str):
    if ":" not in image_name:
        image_name += ":latest"
    # attach the fragment to the image
    arg_list = [
        "oras",
        "attach",
        "--artifact-type",
        ARTIFACT_TYPE,
        image_name,
        filename + ":application/cose-x509+rego"
    ]
    item = call_oras_cli(arg_list, check=False)
    if item.returncode != 0:
        eprint(f"Could not attach fragment to image: {image_name}. Failed with {item.stderr}")

    # regex to extract the digest from the output
    digest_result = re.search(r" sha256:[a-f0-9]{64}", item.stdout.decode("utf8"))
    if digest_result is None:
        print("Attached fragment to image, but could not extract digest from output.")
    digest = digest_result.group(0)
    print(f"Fragment attached to image '{image_name}' with Digest:{digest}")


def generate_imports_from_image_name(image_name: str, minimum_svn: str) -> List[dict]:
    cose_proxy = CoseSignToolProxy()
    image_exists, fragment_hashes = discover(image_name)
    import_list = []

    if image_exists:
        for fragment_hash in fragment_hashes:
            filename = ""
            try:
                filename = pull(image_name, fragment_hash)
                import_statement = cose_proxy.generate_import_from_path(filename, minimum_svn)
                if import_statement not in import_list:
                    import_list.append(import_statement)
            finally:
                # clean up the fragment file
                delete_silently(filename)

    return import_list


# used for standalone fragments
def push_fragment_to_registry(feed_name: str, filename: str) -> None:
    # push the fragment to the registry
    arg_list = [
        "oras",
        "push",
        feed_name,
        "--artifact-type",
        ARTIFACT_TYPE,
        filename + ":application/cose-x509+rego"
    ]
    item = call_oras_cli(arg_list, check=False)
    if item.returncode != 0:
        eprint(f"Could not push fragment to registry: {feed_name}. Failed with {item.stderr}")
    print(f"Fragment pushed to registry '{feed_name}'")
