# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import docker
import functools


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


def get_image_platform(image_reference: str) -> str:
    return "/".join([
        pull_image(image_reference).attrs['Os'],
        pull_image(image_reference).attrs['Architecture']
    ])
