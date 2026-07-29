# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import functools
import logging
import subprocess
import docker

from pathlib import Path

logger = logging.getLogger(__name__)


SUPPORTED_PLATFORMS = [
    "linux/amd64",
    "windows/amd64",
]


@functools.lru_cache()
def pull_image(image_reference: str) -> docker.models.images.Image:
    client = docker.from_env()

    for platform in SUPPORTED_PLATFORMS:
        try:
            image = client.images.pull(image_reference, platform=platform)
            return image
        except (docker.errors.ImageNotFound, docker.errors.NotFound):
            continue

    raise ValueError(f"Image '{image_reference}' not found for any supported platform: {SUPPORTED_PLATFORMS}")


@functools.lru_cache()
def get_image(image_ref: str) -> docker.models.images.Image:

    client = docker.from_env()

    try:
        image = client.images.get(image_ref)
    except docker.errors.ImageNotFound:
        client.images.pull(image_ref)

    image = client.images.get(image_ref)
    return image


def get_image_platform(image_reference: str) -> str:
    """Return the platform of the pulled image (e.g. 'linux/amd64')."""
    return "/".join([
        pull_image(image_reference).attrs['Os'],
        pull_image(image_reference).attrs['Architecture']
    ])


def get_image_layers(image: str, platform: str = "linux/amd64") -> list[str]:

    binary_path = Path(__file__).parent.parent / "bin" / "dmverity-vhd"

    get_image(image)

    arg_list = [binary_path.as_posix(), "-d", "roothash", "-i", image]

    if platform:
        arg_list += ["--platform", platform]

    result = subprocess.run(
        arg_list,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=True,
        text=True,
    )

    stdout_str = result.stdout.strip()

    # Try JSON output first (newer dmverity-vhd versions)
    if stdout_str.startswith("{"):
        try:
            import json
            json_output = json.loads(stdout_str)
            return json_output.get("layers", [])
        except json.JSONDecodeError:
            pass

    # Fallback: line-by-line parsing for older versions
    layers = []
    for line in stdout_str.splitlines():
        if "hash: " in line:
            layers.append(line.split("hash: ")[-1])
        else:
            logger.warning("Unexpected dmverity-vhd output: %s", line)

    return layers


def get_image_config(image: str) -> dict:

    image_config = get_image(image).attrs.get("Config")

    config = {}

    if image_config.get("Cmd") or image_config.get("Entrypoint"):
        config["command"] = (
            image_config.get("Entrypoint") or [] +
            image_config.get("Cmd") or []
        )

    if image_config.get("Env"):
        config["env_rules"] = [{
            "pattern": p,
            "strategy": "string",
            "required": False,
        } for p in image_config.get("Env")]

    if image_config.get("WorkingDir"):
        config["working_dir"] = image_config.get("WorkingDir")

    if image_config.get("StopSignal"):
        config["signals"] = [3]

    return config
