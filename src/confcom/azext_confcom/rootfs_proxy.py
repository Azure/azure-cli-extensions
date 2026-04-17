# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import hashlib
import json
import os
import platform
import stat
import subprocess
import sys
from typing import List, Dict

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
        "url": "https://github.com/microsoft/integrity-vhd/releases/download/v2.0/dmverity-vhd",
        "sha256": "e7ad858fef018acd7d8a4ccb74f1b7a9cc1b3d6db5a7f8da5a259f71b26c12ea",
    },
    "Windows": {
        "path": _binaries_dir / "dmverity-vhd.exe",
        "url": "https://github.com/microsoft/integrity-vhd/releases/download/v2.0/dmverity-vhd.exe",
        "sha256": "6ef425c4bd07739d9cc90e57488985c1fca41f8d106fc816123b95b6305ee0af",
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

    def get_policy_image_layers(  # pylint: disable=redefined-outer-name
        self,
        image: str,
        tag: str,
        platform: str = "linux/amd64",
        tar_location: str = "",
        faster_hashing=False
    ) -> Dict[str, List[str]]:
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

        if platform.startswith("windows"):
            arg_list += ["--platform", platform]

        item = subprocess.run(
            arg_list,
            capture_output=True,
            check=False,
        )

        result = {}
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
            stdout_str = item.stdout.decode("utf8").strip()

            # Try parsing as JSON (both Linux and Windows now output JSON)
            if stdout_str.startswith("{"):
                try:
                    json_output = json.loads(stdout_str)
                    result["layers"] = json_output.get("layers", [])
                    # mounted_cim is only present for Windows
                    if "mounted_cim" in json_output:
                        result["mounted_cim"] = json_output["mounted_cim"]
                except json.JSONDecodeError as e:
                    logger.error("Failed to parse JSON output: %s", e)
                    sys.exit(1)
            else:
                # Fallback: line-by-line parsing for older dmverity-vhd versions
                lines = stdout_str.split("\n")
                layers = [i.split(": ", 1)[1] for i in lines if len(i.split(": ", 1)) > 1]
                result["layers"] = layers
        else:
            eprint(
                "Could not get layer hashes"
            )

        # cache output
        self.layer_cache[image_name] = result
        return result
