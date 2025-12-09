# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import fcntl
import importlib
import json
import os
import subprocess
import tempfile
import psutil
import pytest
import sys
import shutil
import zipfile

from pathlib import Path


CONFCOM_DIR = Path(__file__).parent.parent.parent
SAMPLES_DIR = CONFCOM_DIR / "samples"


# This fixture ensures tests are run against final built wheels of the extension
# instead of the unbuilt local code, which may have breaking differences with
# the thing we actually ship to users. All but the test modules themselves are
# replaced with the wheel in case the tests themselves rely on unshipped code.
@pytest.fixture(autouse=True, scope="session")
def run_on_wheel(request):

    modules_to_test = {i.module for i in request.session.items}
    extensions_to_build = {module.__name__.split(".")[0] for module in modules_to_test}
    extension_dirs = {Path(a.split("/azext_")[0]) for a in request.config.args}

    # Azdev doesn't respect the session scope of the fixture, therefore we need
    # to implement equivalent behaviour by getting a unique ID for the current
    # run and using that to determine if wheels have already been built. Search
    # process parentage until we find the first shell process and use it's
    # child's PID as the run ID.
    process = psutil.Process(os.getpid())
    ancestors = []
    while process.parent() is not None:
        ancestors.insert(0, process)
        process = process.parent()
    RUN_ID = next(p.pid for p in ancestors if any("py" in c for c in p.cmdline()))

    build_dir = Path(tempfile.gettempdir()) / f"wheels_{RUN_ID}"
    build_dir.mkdir(exist_ok=True)

    # Build all extensions being tested into wheels
    for extension in extensions_to_build:

        extension_name = extension.replace("azext_", "")

        # Ensure we acquire a lock while operating on the build dir to avoid races
        lock_file = build_dir / ".dir.lock"
        with lock_file.open("w") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:

                # Delete the extensions build dir, as azdev extension build doesn't
                # reliably handle changes
                for extension_dir in extension_dirs:
                    if (extension_dir / "build").exists():
                        shutil.rmtree((extension_dir / "build").as_posix(), ignore_errors=True)

                if not any(build_dir.glob(f"*{extension_name}*.whl")):
                    subprocess.run(
                        ["azdev", "extension", "build", extension_name, "--dist-dir", build_dir.as_posix()],
                        check=True,
                    )

            finally:
                fcntl.flock(f, fcntl.LOCK_UN)

    # Add the wheel to the path and reload extension modules so the
    # tests pick up the wheel code over the unbuilt code
    wheel_path = next(build_dir.glob("*.whl"))

    expanded_dir = build_dir / f"{wheel_path.stem}_expanded"
    if not expanded_dir.exists():
        expanded_dir.mkdir(exist_ok=True)
        with zipfile.ZipFile(wheel_path, "r") as z:
            z.extractall(expanded_dir)

    sys.path.insert(0, expanded_dir.resolve().as_posix())
    for module in list(sys.modules.values()):
        if (
            extension in module.__name__ and
            not any (m.__name__.startswith(module.__name__) for m in modules_to_test)
        ):
            del sys.modules[module.__name__]
            importlib.import_module(module.__name__)

    yield


@pytest.fixture()
def docker_image():

    registry_id = subprocess.run(
        ["docker", "run", "-d", "-p", "0:5000", "registry:2"],
        stdout=subprocess.PIPE,
        text=True,
    ).stdout

    registry_port = subprocess.run(
        ["docker", "port", registry_id],
        stdout=subprocess.PIPE,
        text=True,
    ).stdout.split(":")[-1].strip()

    test_container_ref = f"localhost:{registry_port}/hello-world:latest"
    subprocess.run(["docker", "pull", "hello-world"])
    subprocess.run(["docker", "tag", "hello-world", test_container_ref])
    subprocess.run(["docker", "push", test_container_ref])

    with tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8", delete=True) as temp_file:
        json.dump({
            "version": "1.0.0",
            "containers": [
                {
                    "name": "hello-world",
                    "properties": {
                        "image": test_container_ref,
                    },
                }
            ]
        }, temp_file)
        temp_file.flush()

        yield test_container_ref, temp_file.name

    subprocess.run(["docker", "stop", registry_id])


@pytest.fixture(scope="session")
def cert_chain():
    with tempfile.TemporaryDirectory() as temp_dir:
        subprocess.run(
            [
                (SAMPLES_DIR / "certs" / "create_certchain.sh").as_posix(),
                temp_dir
            ],
            check=True,
        )
        yield temp_dir
