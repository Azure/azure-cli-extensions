# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import importlib
from pathlib import Path
import subprocess
import tempfile
import pytest
import sys
import shutil


# This fixture ensures tests are run against final built wheels of the extension
# instead of the unbuilt local code, which may have breaking differences with
# the thing we actually ship to users. All but the test modules themselves are
# replaced with the wheel in case the tests themselves rely on unshipped code.


@pytest.fixture(autouse=True, scope="session")
def run_on_wheel(request):

    modules_to_test = {i.module for i in request.session.items}
    extensions_to_build = {module.__name__.split(".")[0] for module in modules_to_test}
    extension_dirs = {Path(a.split("/azext_")[0]) for a in request.config.args}

    with tempfile.TemporaryDirectory(delete=True) as build_dir:

        # Delete the extensions build dir, as azdev extension build doesn't
        # reliably handle changes
        for extension_dir in extension_dirs:
            if (extension_dir / "build").exists():
                shutil.rmtree((extension_dir / "build").as_posix(), ignore_errors=True)

        # Build all extensions being tested into wheels
        for extension in extensions_to_build:
            subprocess.run(
                ["azdev", "extension", "build", extension.replace("azext_", ""), "--dist-dir", build_dir],
                check=True,
            )

            # Add the wheel to the path and reload extension modules so the
            # tests pick up the wheel code over the unbuilt code
            sys.path.insert(0, Path(build_dir).glob("*.whl").__next__().as_posix())
            for module in list(sys.modules.values()):
                if extension in module.__name__ and module not in modules_to_test:
                    del sys.modules[module.__name__]
                    importlib.import_module(module.__name__)

        yield

