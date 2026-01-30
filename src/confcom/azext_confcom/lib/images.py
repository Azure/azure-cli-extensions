# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import functools
import subprocess
import docker

from pathlib import Path


@functools.lru_cache()
def get_image(image_ref: str) -> docker.models.images.Image:

    client = docker.from_env()

    try:
        image = client.images.get(image_ref)
    except docker.errors.ImageNotFound:
        client.images.pull(image_ref)

    image = client.images.get(image_ref)
    return image


def get_image_layers(image: str) -> list[str]:

    binary_path = Path(__file__).parent.parent / "bin" / "dmverity-vhd"

    get_image(image)
    result = subprocess.run(
        [binary_path.as_posix(), "-d", "roothash", "-i", image],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=True,
        text=True,
    )

    return [line.split("hash: ")[-1] for line in result.stdout.splitlines()]


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
