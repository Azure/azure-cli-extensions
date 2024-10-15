# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import subprocess
from typing import List
import os
import sys
import stat
from pathlib import Path
import platform
import requests
from knack.log import get_logger
from azext_confcom.errors import eprint


host_os = platform.system()
machine = platform.machine()
logger = get_logger(__name__)


class SecurityPolicyProxy:  # pylint: disable=too-few-public-methods
    # static variable to cache layer hashes between container groups
    layer_cache = {}

    @staticmethod
    def download_binaries():
        dir_path = os.path.dirname(os.path.realpath(__file__))

        bin_folder = os.path.join(dir_path, "bin")
        if not os.path.exists(bin_folder):
            os.makedirs(bin_folder)

        # get the most recent release artifacts from github
        r = requests.get("https://api.github.com/repos/microsoft/hcsshim/releases")
        bin_flag = False
        exe_flag = False
        # search for dmverity-vhd in the assets from hcsshim releases
        for release in r.json():
            # these should be newest to oldest
            for asset in release["assets"]:
                # download the file if it contains dmverity-vhd
                if "dmverity-vhd" in asset["name"]:
                    if "exe" in asset["name"]:
                        exe_flag = True
                    else:
                        bin_flag = True
                    # get the download url for the dmverity-vhd file
                    exe_url = asset["browser_download_url"]
                    # download the file
                    r = requests.get(exe_url)
                    # save the file to the bin folder
                    with open(os.path.join(bin_folder, asset["name"]), "wb") as f:
                        f.write(r.content)
            if bin_flag and exe_flag:
                break

    def __init__(self):
        script_directory = os.path.dirname(os.path.realpath(__file__))
        DEFAULT_LIB = "./bin/dmverity-vhd"

        if host_os == "Linux":
            pass
        elif host_os == "Windows":
            if machine.endswith("64"):
                DEFAULT_LIB += ".exe"
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

    def get_policy_image_layers(
        self,
        image: str,
        tag: str,
        tar_location: str = "",
        faster_hashing=False
    ) -> List[str]:
        image_name = f"{image}:{tag}"
        # populate layer info
        if self.layer_cache.get(image_name):
            return self.layer_cache.get(image_name)

        policy_bin_str = str(self.policy_bin)

        arg_list = [
            f"{policy_bin_str}",
        ]

        # decide if we're reading from a tarball or not
        if tar_location:
            arg_list += ["--tarball", tar_location]
        else:
            arg_list += ["-d"]

        if not tar_location and faster_hashing:
            arg_list += ["-b"]

        # add the image to the end of the parameter list
        arg_list += ["roothash", "-i", f"{image_name}"]

        item = subprocess.run(
            arg_list,
            capture_output=True,
            check=False,
        )

        output = []
        if item.returncode != 0:
            if item.stderr.decode("utf-8") != "" and item.stderr.decode("utf-8") is not None:
                logger.warning(item.stderr.decode("utf-8"))
            if item.returncode == -9:
                logger.warning(
                    "System does not have enough memory to calculate layer hashes for image: %s. %s",
                    image_name,
                    "Please try increasing the amount of system memory."
                )
            sys.exit(item.returncode)
        elif len(item.stdout) > 0:
            output = item.stdout.decode("utf8").strip("\n").split("\n")
            output = [i.split(": ", 1)[1] for i in output if len(i.split(": ", 1)) > 1]
        else:
            eprint(
                "Could not get layer hashes"
            )

        # cache output layers
        self.layer_cache[image_name] = output
        return output
