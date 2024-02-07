# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path

from knack.log import get_logger

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


def create_bicep_from_template():
    # Take j2 template, take params, return bicep file
    return NotImplementedError


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
            tar.extractall(path=target_dir)
    elif file_extension == ".tar":
        with tarfile.open(file_path, "r:") as tar:
            tar.extractall(path=target_dir)
    else:
        raise InvalidFileTypeError(
            f"ERROR: The helm package, '{file_path}', is not"
            "a .tgz, .tar or .tar.gz file."
        )

    return Path(target_dir, os.listdir(target_dir)[0])


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
