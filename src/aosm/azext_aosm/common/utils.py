# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
import re
import os
import shutil
import subprocess
import tarfile
import tempfile
from typing import Tuple
from time import sleep
from pathlib import Path
from jinja2 import StrictUndefined, Template
from knack.log import get_logger
from knack.util import CLIError
from azure.cli.core.azclierror import BadRequestError, ClientRequestError

from azext_aosm.common.constants import NEXUS_IMAGE_REGEX
from azext_aosm.common.exceptions import InvalidFileTypeError, MissingDependency

logger = get_logger(__name__)


def convert_bicep_to_arm(bicep_template_path: Path) -> dict:
    """
    Convert a bicep template into an ARM template.

    :param bicep_template_path: The path to the bicep template to be converted
    :return: Output dictionary representation of the ARM template JSON.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        bicep_filename = bicep_template_path.name
        arm_template_name = bicep_filename.replace(".bicep", ".json")
        arm_path = Path(tmpdir) / arm_template_name
        logger.debug(
            "Converting bicep template %s to ARM.",
            bicep_template_path,
        )

        try:
            subprocess.run(
                [
                    str(shutil.which("az")),
                    "bicep",
                    "build",
                    "--file",
                    bicep_template_path,
                    "--outfile",
                    str(arm_path),
                ],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except subprocess.CalledProcessError as error:
            raise RuntimeError(
                f"Bicep to ARM template compilation failed.\n{error.stderr}"
            )

        logger.debug("ARM template:\n%s", arm_path.read_text())
        arm_json = json.loads(arm_path.read_text())

    return arm_json


def render_bicep_contents_from_j2(template_path: Path, params):
    """Write the definition bicep file from given template."""
    with open(template_path, "r", encoding="UTF-8") as f:
        template: Template = Template(
            f.read(),
            undefined=StrictUndefined,
        )

    bicep_contents: str = template.render(params)
    return bicep_contents


def get_template_path(definition_type: str, template_name: str) -> Path:
    """Get the path to a template."""
    return (
        Path(__file__).parent.parent
        / "common"
        / "templates"
        / definition_type
        / template_name
    )


def extract_tarfile(file_path: Path, target_dir: Path) -> Path:
    """
    Extracts the tar file to a temporary directory.
    Args:
        file_path: Path to the tar file.
    Returns:
        Path to the temporary directory.
    """
    file_extension = file_path.suffix

    if file_extension in (".gz", ".tgz"):
        with tarfile.open(file_path, "r:gz") as tar:
            safe_extract(tar, path=target_dir)
    elif file_extension == ".tar":
        with tarfile.open(file_path, "r:") as tar:
            safe_extract(tar, path=target_dir)
    else:
        raise InvalidFileTypeError(
            f"ERROR: The helm package, '{file_path}', is not"
            "a .tgz, .tar or .tar.gz file."
        )

    return Path(target_dir, os.listdir(target_dir)[0])


def is_within_directory(directory, target):
    """
    Ensure the target path is within the intended directory
    """
    abs_directory = os.path.abspath(directory)
    abs_target = os.path.abspath(target)
    return os.path.commonpath([abs_directory]) == os.path.commonpath([abs_directory, abs_target])


def safe_extract(tar, path="."):
    """
    Validates each file's path before extraction to prevent malicious files from escaping the target directory
    """
    for member in tar.getmembers():
        member_path = os.path.join(path, member.name)
        if not is_within_directory(path, member_path):
            raise Exception("Attempted Path Traversal in Tar File")  # pylint: disable=broad-exception-raised
    tar.extractall(path)


def snake_case_to_camel_case(text):
    """Converts snake case to camel case."""
    components = text.split("_")
    return components[0] + "".join(x[0].upper() + x[1:] for x in components[1:])


def check_tool_installed(tool_name: str) -> None:
    """
    Check whether a tool such as docker or helm is installed.

    :param tool_name: name of the tool to check, e.g. docker
    """
    if shutil.which(tool_name) is None:
        raise MissingDependency(f"You must install {tool_name} to use this command.")


def call_subprocess_raise_output(cmd: list) -> str:
    """
    Call a subprocess and raise a CLIError with the output if it fails.

    :param cmd: command to run, in list format
    :raise CLIError: if the subprocess fails
    """
    log_cmd = cmd.copy()
    if "--password" in log_cmd:
        # Do not log out passwords.
        log_cmd[log_cmd.index("--password") + 1] = "[REDACTED]"

    try:
        called_process = subprocess.run(
            cmd, encoding="utf-8", capture_output=True, text=True, check=True
        )
        logger.debug(
            "Output from %s: %s. Error: %s",
            log_cmd,
            called_process.stdout,
            called_process.stderr,
        )

        return called_process.stdout
    except subprocess.CalledProcessError as error:
        all_output: str = (
            f"Command: {' '.join(log_cmd)}\n"
            f"stdout: {error.stdout}\n"
            f"stderr: {error.stderr}\n"
            f"Return code: {error.returncode}"
        )
        logger.debug("The following command failed to run:\n%s", all_output)
        # Raise the error without the original exception, which may contain secrets.
        raise CLIError(all_output) from None


def clean_registry_name(registry_name: str) -> str:
    """Remove https:// from the registry name."""
    return registry_name.replace("https://", "")


def push_image_from_local_registry_to_acr(
    target_acr: str,
    target_image: str,
    target_username: str,
    target_password: str,
    local_docker_image: str,
) -> None:
    """
    Push image to target registry using docker push. Requires docker.

    :param target_acr: name of the target Azure Container registry
        e.g. targetacr.azurecr.io
    :type target_acr: str
    :param target_image: name of the target image (namespace/repository:tag)
        e.g. namespace/nginx:1.0.0
    :type target_image: str
    :param target_username: username for the target ACR
    :type target_username: str
    :param target_password: password for the target ACR
    :type target_password: str
    :param local_docker_image: name and tag of the source image on local registry
        e.g. uploadacr.azurecr.io/samples/nginx:stable
    :type local_docker_image: str
    """

    target = f"{target_acr}/{target_image}"
    logger.debug("Target ACR: %s", target)

    # To push the image to the target registry, we need to tag the source image
    logger.info("Tagging source image %s as %s", local_docker_image, target)
    tag_image_cmd = [
        str(shutil.which("docker")),
        "tag",
        local_docker_image,
        target,
    ]
    call_subprocess_raise_output(tag_image_cmd)

    login_to_artifact_store_registry(target_acr, target_username, target_password)

    try:
        logger.info("Pushing target image %s using docker push", target)
        push_target_image_cmd = [
            str(shutil.which("docker")),
            "push",
            target,
        ]
        call_subprocess_raise_output(push_target_image_cmd)
    except CLIError as error:
        logger.debug(error, exc_info=True)
        raise ClientRequestError(
            f"Failed to push {local_docker_image} to {target_acr}."
        ) from error
    finally:
        docker_logout_cmd = [
            str(shutil.which("docker")),
            "logout",
            target_acr,
        ]
        call_subprocess_raise_output(docker_logout_cmd)


def login_to_artifact_store_registry(
    registry: str, username: str, password: str
) -> None:
    """
    Log in to the registry using az acr login.

    :param registry: The registry to log in to
    :param username: The username to use for logging in
    :param password: The password to use for logging in
    """
    logger.info("Logging into artifact store registry %s", registry)
    # ACR login seems to work intermittently, so we retry on failure
    retries = 0
    while True:
        try:
            target_acr_login_cmd = [
                str(shutil.which("az")),
                "acr",
                "login",
                "--name",
                registry,
                "--username",
                username,
                "--password",
                password,
            ]
            call_subprocess_raise_output(target_acr_login_cmd)
            logger.debug("Logged in to %s", registry)
            break
        except CLIError as error:
            if retries < 20:
                logger.info("Retrying ACR login. Retries so far: %s", retries)
                retries += 1
                sleep(3)
                continue
            logger.debug(error, exc_info=True)

            raise BadRequestError(
                f"Failed to login to {registry} as {username}."
            ) from error


def split_image_path(image) -> Tuple[str, str, str]:
    """Split the image path into source acr registry, name and version."""
    (source_acr_registry, name_and_version) = image.split("/", 2)
    (name, version) = name_and_version.split(":", 2)
    return (source_acr_registry, name, version)


def is_valid_nexus_image_version(string):
    """Check if image version is valid.

    This is based on validation in pez repo.
    It requires the image version to be major.minor.patch,
    but does not enforce full semver validation.
    """

    return re.match(NEXUS_IMAGE_REGEX, string) is not None


def append_text(path, text, encoding=None, errors=None):
    with path.open("a+", encoding=encoding, errors=errors) as f:
        f.write(text)


def generate_data_for_given_schema(schema_definition):
    generated_data = generate_data(schema_definition)
    return generated_data


def generate_data(schema_definition):
    schema = json.loads(schema_definition)
    if 'default' in schema:
        return schema['default']
    result = ''  # Initialize a variable to hold the return value
    if schema['type'] == 'object':
        obj = {}
        properties = schema.get('properties', {})
        for key, subschema in properties.items():
            obj[key] = generate_data(json.dumps(subschema))
        result = obj
    if schema['type'] == 'array':
        items_schema = schema.get('items')
        if items_schema:
            result = [generate_data(json.dumps(items_schema)) for _ in range(schema.get('minItems', 1))]
        else:
            result = []
    return result
