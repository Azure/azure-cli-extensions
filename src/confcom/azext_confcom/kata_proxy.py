# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from pathlib import Path
import platform
import stat
import subprocess
import sys

import requests
from azext_confcom.config import DATA_FOLDER
from azext_confcom.errors import eprint
from azext_confcom.lib.paths import get_binaries_dir, get_data_dir

host_os = platform.system()
machine = platform.machine()


_binaries_dir = get_binaries_dir()
_kata_binaries = {
    "Linux": {
        "path": _binaries_dir / "genpolicy-linux",
        "url": "https://github.com/microsoft/kata-containers/releases/download/3.2.0.azl3.genpolicy3/genpolicy",
    },
    "Windows": {
        "path": _binaries_dir / "genpolicy-windows.exe",
        "url": "https://github.com/microsoft/kata-containers/releases/download/3.2.0.azl1.genpolicy0/genpolicy.exe",
    },
}
_data_dir = get_data_dir()
_kata_data = [
    {
        "path": _data_dir / "genpolicy-settings.json",
        "url": "https://github.com/microsoft/kata-containers/releases/download/3.2.0.azl3.genpolicy3/genpolicy-settings.json",
    },
    {
        "path": _data_dir / "rules.rego",
        "url": "https://github.com/microsoft/kata-containers/releases/download/3.2.0.azl3.genpolicy3/rules.rego",
    },
]


class KataPolicyGenProxy:  # pylint: disable=too-few-public-methods
    # static variable to cache layer hashes between container groups
    layer_cache = {}

    @staticmethod
    def download_binaries():

        for binary_info in list(_kata_binaries.values()) + _kata_data:
            kata_fetch_resp = requests.get(binary_info["url"], verify=True)
            kata_fetch_resp.raise_for_status()

            with open(binary_info["path"], "wb") as f:
                f.write(kata_fetch_resp.content)

    def __init__(self):
        script_directory = os.path.dirname(os.path.realpath(__file__))
        DEFAULT_LIB = "./bin/genpolicy"

        if host_os == "Linux":
            DEFAULT_LIB += "-linux"
        elif host_os == "Windows":
            eprint("The katapolicygen subcommand for Windows has not been implemented.")
        elif host_os == "Darwin":
            eprint("The katapolicygen subcommand for MacOS has not been implemented.")
        else:
            eprint(
                "Unknown target platform. The katapolicygen subcommand only works with Linux"
            )

        self.policy_bin = os.path.join(f"{script_directory}", f"{DEFAULT_LIB}")

        # check if the extension binary exists
        if not os.path.exists(self.policy_bin):
            eprint("The katapolicygen subcommand binary file cannot be located.")
        if not os.access(self.policy_bin, os.X_OK):
            # add executable permissions for the current user if they don't exist
            st = os.stat(self.policy_bin)
            os.chmod(self.policy_bin, st.st_mode | stat.S_IXUSR)

    def kata_genpolicy(
        self,
        yaml_path,
        config_map_file=None,
        outraw=False,
        print_policy=False,
        use_cached_files=False,
        settings_file_name=None,
        rules_file_name=None,
        print_version=False,
        containerd_pull=False,
        containerd_socket_path=None
    ) -> list[str]:
        policy_bin_str = str(self.policy_bin)
        # get path to data and rules folder
        arg_list = [policy_bin_str]

        if yaml_path:
            arg_list.append("-y")
            arg_list.append(yaml_path)

        if config_map_file is not None:
            arg_list.append("-c")
            arg_list.append(config_map_file)

        if outraw:
            arg_list.append("-r")

        if print_policy:
            arg_list.append("-b")

        if use_cached_files:
            arg_list.append("-u")

        arg_list.append("-j")
        if settings_file_name:
            arg_list.append(settings_file_name)
        else:
            arg_list.append(os.path.join(DATA_FOLDER, "genpolicy-settings.json"))

        arg_list.append("-p")
        if rules_file_name:
            arg_list.append(rules_file_name)
        else:
            arg_list.append(os.path.join(DATA_FOLDER, "rules.rego"))

        if print_version:
            arg_list.append("-v")

        if containerd_pull:
            item_to_append = "-d"
            # -d by itself will use default path: /var/run/containerd/containerd.sock
            # -d=my/path/my_containerd.sock will use the specified path
            if containerd_socket_path:
                item_to_append += f"={containerd_socket_path}"
            arg_list.append(item_to_append)

        item = subprocess.run(
            arg_list,
            check=False,
        )

        # get the exit code from the subprocess
        if item.returncode != 0:
            sys.exit(item.returncode)

        # decode the output
        output = item.stdout.decode("utf8") if item.stdout is not None else ""
        return output
