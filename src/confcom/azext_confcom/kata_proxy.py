# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import subprocess
from typing import List
import os
import stat
import sys
from pathlib import Path
import platform
import requests
from azext_confcom.config import DATA_FOLDER
from azext_confcom.errors import eprint


host_os = platform.system()
machine = platform.machine()


class KataPolicyGenProxy:  # pylint: disable=too-few-public-methods
    # static variable to cache layer hashes between container groups
    layer_cache = {}

    @staticmethod
    def download_binaries():
        dir_path = os.path.dirname(os.path.realpath(__file__))

        bin_folder = os.path.join(dir_path, "bin")
        if not os.path.exists(bin_folder):
            os.makedirs(bin_folder)

        data_folder = os.path.join(dir_path, "data")
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)

        # get the most recent release artifacts from github
        r = requests.get("https://api.github.com/repos/microsoft/kata-containers/releases")
        bin_flag = False
        needed_assets = ["genpolicy", "genpolicy.exe"]
        # search for genpolicy in the assets from kata-container releases
        for release in r.json():
            if "genpolicy" in release.get("tag_name"):
                # these should be newest to oldest
                for asset in release["assets"]:
                    # download the file if it contains genpolicy
                    if asset["name"] in needed_assets:
                        save_name = ""
                        if ".exe" in asset["name"]:
                            save_name = "genpolicy-windows.exe"
                        else:
                            save_name = "genpolicy-linux"
                        bin_flag = True
                        # get the download url for the genpolicy file
                        exe_url = asset["browser_download_url"]
                        # download the file
                        r = requests.get(exe_url)
                        # save the file to the bin folder
                        with open(os.path.join(bin_folder, save_name), "wb") as f:
                            f.write(r.content)

                    # download the rules.rego and genpolicy-settings.json files
                    if asset["name"] == "rules.rego" or asset["name"] == "genpolicy-settings.json":
                        # download the rules.rego file
                        exe_url = asset["browser_download_url"]
                        # download the file
                        r = requests.get(exe_url)
                        # save the file to the data folder
                        with open(os.path.join(data_folder, asset["name"]), "wb") as f:
                            f.write(r.content)
            if bin_flag:
                break

    def __init__(self):
        script_directory = os.path.dirname(os.path.realpath(__file__))
        DEFAULT_LIB = "./bin/genpolicy"

        if host_os == "Linux":
            DEFAULT_LIB += "-linux"
        elif host_os == "Windows":
            if machine.endswith("64"):
                DEFAULT_LIB += "-windows.exe"
            else:
                eprint(
                    "32-bit Windows is not supported."
                )
        elif host_os == "Darwin":
            eprint("The extension for MacOS has not been implemented.")
        else:
            eprint(
                "Unknown target platform. The extension only works with Windows, Linux and MacOS"
            )

        self.policy_bin = Path(os.path.join(f"{script_directory}", f"{DEFAULT_LIB}"))

        # check if the extension binary exists
        if not os.path.exists(self.policy_bin):
            eprint("The extension binary file cannot be located.")
        if not os.access(self.policy_bin, os.X_OK):
            # add executable permissions for the current user if they don't exist
            st = os.stat(self.policy_bin)
            os.chmod(self.policy_bin, st.st_mode | stat.S_IXUSR)

    def kata_genpolicy(
        self, yaml_path,
        config_map_file=None,
        outraw=False,
        print_policy=False,
        use_cached_files=False,
        settings_file_name=None,
    ) -> List[str]:
        policy_bin_str = str(self.policy_bin)
        # get path to data and rules folder
        arg_list = [policy_bin_str, "-y", yaml_path, "-i", DATA_FOLDER]

        if config_map_file is not None:
            arg_list.append("-c")
            arg_list.append(config_map_file)

        if outraw:
            arg_list.append("-r")

        if print_policy:
            arg_list.append("-b")

        if use_cached_files:
            arg_list.append("-u")

        if settings_file_name:
            arg_list.append("-j")
            # only take the last part of the path for the settings file
            settings_file_name = os.path.basename(settings_file_name)
            arg_list.append(settings_file_name)

        item = subprocess.run(
            arg_list,
            # stdout=sys.stdout,
            # stderr=sys.stderr,
            check=False,
        )

        # get the exit code from the subprocess
        if item.returncode != 0:
            sys.exit(item.returncode)

        # decode the output
        output = item.stdout.decode("utf8") if item.stdout is not None else ""
        return output
