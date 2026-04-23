# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

import os
import sys
from shutil import rmtree
from subprocess import CalledProcessError, check_call

IS_WINDOWS = os.name == "nt"


def run(command, shell=False):
    try:
        print("Executing: " + command)
        print(command.split())
        check_call(command.split(), cwd=root_dir, shell=shell)
        print()
    except CalledProcessError as err:
        print(err, file=sys.stderr)
        sys.exit(1)


def pip_install(instruction):
    bin_path = "Scripts" if IS_WINDOWS else "bin"
    pip_path = os.path.join(root_dir, "env", bin_path, "pip")
    run(pip_path + " install " + instruction)


root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", ".."))
extension_dir = os.path.join(root_dir, "arcdata")
azure_dir = os.getenv("AZURE_CONFIG_DIR", None) or os.path.expanduser(
    os.path.join("~", ".azure")
)

print("Running dev setup...")
print("Root directory '{}'\n".format(root_dir))
print("Extension directory '{}'\n".format(extension_dir))
print("Azure root directory '{}'\n".format(azure_dir))

# enforce AZURE_EXTENSION_DIR=arcdata/projects/azure-cli-extension
run(
    "{prefix} AZURE_EXTENSION_DIR={root_dir}".format(
        prefix="set" if IS_WINDOWS else "export", root_dir=root_dir
    ),
    shell=True,
)

# set up clean virtual env and activate
rmtree(os.path.join(root_dir, "env"), ignore_errors=True)
run(
    "{cmd} -m venv {venv}".format(
        cmd="python" if IS_WINDOWS else "python3",
        venv=os.path.join(root_dir, "env"),
    )
)

try:
    pip_install("--upgrade pip")
except:
    # skipping "ERROR: Could not install packages due to an OSError:
    # [WinError 5] Access is denied", pip was upgraded despite the error.
    pass

# Install all dev packages and ext source
pip_install("-r {}".format(os.path.join(root_dir, "dev-requirements.txt")))
pip_install("-e {}".format(os.path.join(root_dir, "tools", "pytest-az")))
pip_install("-e {}".format(extension_dir))

run(
    "{cmd} install".format(
        cmd=os.path.join(
            root_dir, "env", "Scripts" if IS_WINDOWS else "bin", "pre-commit"
        )
    )
)

print(
    "Finished dev setup. Remember to activate your venv and set in "
    "your shell:"
)
if IS_WINDOWS:
    print(".\env\Scripts\\activate.bat")
    print("set AZURE_EXTENSION_DIR=%cd%")
else:
    print("source ./env/bin/activate")
    print("export AZURE_EXTENSION_DIR=$(pwd)")
