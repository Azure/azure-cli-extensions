# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import subprocess
import json
import platform
import re
from knack.log import get_logger
from typing import List
from azext_confcom.errors import eprint
from azext_confcom.config import ARTIFACT_TYPE
from azext_confcom.cose_proxy import CoseSignToolProxy
from azext_confcom.os_util import delete_silently

host_os = platform.system()
machine = platform.machine()

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
    if "/" not in name or "." not in name.split("/")[0]:
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
) -> List[str]:
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
        if "401: Unauthorized" in item.stderr.decode("utf-8"):
            eprint(
                f"Error pulling the policy fragment from {image}.\n\n"
                + "Please log into the registry and try again.\n\n"
            )
        eprint(f"Error retrieving fragments from remote repo: {item.stderr.decode('utf-8')}", exit_code=item.returncode)
    return hashes


# pull the policy fragment from the remote repo and return its contents as a string
def pull(
    image: str,
    image_hash: str,
) -> str:
    if "@sha256:" in image:
        image = image.split("@")[0]
    arg_list = ["oras", "pull", f"{image}@{image_hash}"]
    logger.info("Pulling fragment: %s@%s", image, image_hash)
    item = call_oras_cli(arg_list, check=False)

    # get the exit code from the subprocess
    if item.returncode != 0:
        if "401: Unauthorized" in item.stderr.decode("utf-8"):
            eprint(
                f"Error pulling the policy fragment: {image}@{image_hash}.\n\n"
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
        eprint(f"Could not find the filename of the pulled fragment for {image}@{image_hash}")

    return filename


def pull_all_image_attached_fragments(image):
    # TODO: be smart about if we're pulling a fragment directly or trying to discover them from an image tag
    # TODO: this will be for standalone fragments
    fragments = discover(image)
    fragment_contents = []
    feeds = []
    proxy = CoseSignToolProxy()
    for fragment_digest in fragments:
        filename = pull(image, fragment_digest)
        text = proxy.extract_payload_from_path(filename)
        feed = proxy.extract_feed_from_path(filename)
        # containers = extract_containers_from_text(text, REGO_CONTAINER_START)
        # new_fragments = extract_containers_from_text(text, REGO_FRAGMENT_START)
        # if new_fragments:
        #     for new_fragment in new_fragments:
        #         feed = new_fragment.get("feed")
        #         # if we don't have the feed in the list of feeds we've already pulled, pull it
        #         if feed not in fragment_feeds:
        #             fragment_contents.extend(pull_all_image_attached_fragments(feed, fragment_feeds=fragment_feeds))
        fragment_contents.append(text)
        feeds.append(feed)
    return fragment_contents, feeds


def check_oras_cli():
    text = "ORAS CLI not installed. Please install ORAS CLI: https://oras.land/docs/installation"
    try:
        item = call_oras_cli(["oras", "version"], check=False)
        if item.returncode != 0:
            eprint(text)
    except FileNotFoundError:
        eprint(text)


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
    fragment_hashes = discover(image_name)
    import_list = []

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
