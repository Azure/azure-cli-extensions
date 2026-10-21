# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import importlib.util
import os
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from unittest.mock import Mock, call

import pytest


@pytest.fixture
def source_runner(monkeypatch, tmp_path):
    extension = tmp_path / "example extension"
    (extension / "azext_example" / "tests").mkdir(parents=True)
    for variable in ("TRAVIS_COMMIT_RANGE", "ADO_PULL_REQUEST_LATEST_COMMIT",
                     "ADO_PULL_REQUEST_TARGET_BRANCH"):
        monkeypatch.delenv(variable, raising=False)
    utilities = ModuleType("util")
    utilities.SRC_PATH = str(tmp_path)
    monkeypatch.setitem(sys.modules, "util", utilities)
    script = Path(__file__).resolve().parents[2] / "scripts" / "ci" / "test_source.py"
    spec = importlib.util.spec_from_file_location("ci_test_source", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ALL_TESTS = [("azext_example", extension.as_posix())]
    runner = Mock()
    monkeypatch.setattr(module, "run_command", runner)
    return module, runner, extension


@pytest.mark.parametrize("has_requirements", [False, True])
def test_test_dependencies_are_installed_only_when_declared(source_runner, has_requirements):
    module, runner, extension = source_runner
    requirements = extension / "azext_example" / "tests" / "requirements.txt"
    if has_requirements:
        requirements.write_text("jsonschema>=4.0.0,<5\n", encoding="utf-8")

    module.test_extension()

    expected = [call(["azdev", "extension", "add", extension.name], check_return_code=True)]
    if has_requirements:
        expected.append(call(
            [sys.executable, "-m", "pip", "install", "-r",
             os.path.join(extension.as_posix(), "azext_example", "tests", "requirements.txt")],
            check_return_code=True,
        ))
    expected.extend([
        call([sys.executable, "-m", "azdev", "test", "--no-exitfirst", "--discover",
              "--verbose", "azext_example"], check_return_code=True),
        call(["azdev", "extension", "remove", extension.name], check_return_code=True),
    ])
    assert runner.call_args_list == expected


def test_dependency_install_failure_stops_before_discovery(source_runner):
    module, runner, extension = source_runner
    (extension / "azext_example" / "tests" / "requirements.txt").write_text(
        "jsonschema>=4.0.0,<5\n", encoding="utf-8")
    error = subprocess.CalledProcessError(1, ["pip", "install"])
    runner.side_effect = [None, error]

    with pytest.raises(subprocess.CalledProcessError) as raised:
        module.test_extension()

    assert raised.value is error
    assert runner.call_count == 2
    assert runner.call_args.args[0][1:5] == ["-m", "pip", "install", "-r"]
