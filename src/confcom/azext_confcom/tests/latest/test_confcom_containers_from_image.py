# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import tempfile
import docker
import pytest
import portalocker

from contextlib import redirect_stdout
from io import StringIO
from itertools import product
from pathlib import Path
from deepdiff import DeepDiff

from azext_confcom.command.containers_from_image import containers_from_image


TEST_DIR = Path(__file__).parent
CONFCOM_DIR = TEST_DIR.parent.parent.parent
SAMPLES_ROOT = CONFCOM_DIR / "samples" / "images"
DOCKER_LOCK = Path(tempfile.gettempdir()) / "confcom-docker.lock"


@pytest.fixture(scope="session", autouse=True)
def build_test_containers():

    docker_client = docker.from_env()
    with portalocker.Lock(DOCKER_LOCK.as_posix(), timeout=20):
        for image_sample in SAMPLES_ROOT.iterdir():
            docker_client.images.build(
                path=str(image_sample),
                tag=f"confcom_test_{image_sample.name}",
                quiet=True,
                rm=True,
            )

    yield


@pytest.mark.parametrize(
    "sample_directory, platform",
    product(
        [p.name for p in SAMPLES_ROOT.iterdir()],
        ["aci"],
    )
)
def test_containers_from_image(sample_directory: str, platform: str):

    sample_directory = Path(SAMPLES_ROOT) / sample_directory

    expected_container_def_path = sample_directory / f"{platform}_container.inc.rego"
    with expected_container_def_path.open("r", encoding="utf-8") as handle:
        expected_container_def = json.load(handle)

    buffer = StringIO()
    with redirect_stdout(buffer):
        containers_from_image(
            image=f"confcom_test_{sample_directory.name}",
            platform=platform,
        )

    actual_container_def = json.loads(buffer.getvalue())

    diff = DeepDiff(
        actual_container_def,
        expected_container_def,
        ignore_order=True,
    )
    assert diff == {}, diff