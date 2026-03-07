# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import hashlib
import os
import platform
import stat
import subprocess
import sys
from typing import List

import requests
from azext_confcom.errors import eprint
from azext_confcom.lib.paths import get_binaries_dir
from knack.log import get_logger


host_os = platform.system()
machine = platform.machine()
logger = get_logger(__name__)


_binaries_dir = get_binaries_dir()
_dmverity_vhd_binaries = {
    "Linux": {
        "path": _binaries_dir / "dmverity-vhd",
        "url": "https://github.com/microsoft/integrity-vhd/releases/download/v1.6/dmverity-vhd",
        "sha256": "b8cf3fa3594e48070a31aa538d5b4b40d5b33b8ac18bc25a1816245159648fb0",
    },
    "Windows": {
        "path": _binaries_dir / "dmverity-vhd.exe",
        "url": "https://github.com/microsoft/integrity-vhd/releases/download/v1.6/dmverity-vhd.exe",
        "sha256": "ca0f95d798323f3ef26feb036112be9019f5ceaa6233ee2a65218d5a143ae474",
    },
}


class SecurityPolicyProxy:  # pylint: disable=too-few-public-methods
    # static variable to cache layer hashes between container groups
    layer_cache = {}

    @staticmethod
    def download_binaries():

        for binary_info in _dmverity_vhd_binaries.values():
            dmverity_vhd_fetch_resp = requests.get(binary_info["url"], verify=True)
            dmverity_vhd_fetch_resp.raise_for_status()

            assert hashlib.sha256(dmverity_vhd_fetch_resp.content).hexdigest() == binary_info["sha256"]

            with open(binary_info["path"], "wb") as f:
                f.write(dmverity_vhd_fetch_resp.content)

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
                "Unknown target platform. The extension only works with Windows and Linux"
            )

        self.policy_bin = os.path.join(f"{script_directory}", f"{DEFAULT_LIB}")

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
            logger.info("Calculating layer hashes from tarball")
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
