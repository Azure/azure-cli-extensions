# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import subprocess
from typing import List
import os
from pathlib import Path
import platform
from azext_confcom.errors import eprint


host_os = platform.system()
arch = platform.architecture()[0]


class SecurityPolicyProxy:  # pylint: disable=too-few-public-methods
    def __init__(self):
        script_directory = os.path.dirname(os.path.realpath(__file__))
        DEFAULT_LIB = "./bin/dmverity-vhd"

        if host_os == "Linux":
            pass
        elif host_os == "Windows":
            if arch == "64bit":
                DEFAULT_LIB += ".exe"
            else:
                raise NotImplementedError(
                    f"The current architecture {arch} for windows is not supported."
                )
        elif host_os == "Darwin":
            eprint("The extension for MacOS has not been implemented.")
        else:
            eprint(
                "Unknown target platform. The extension only works with Windows, Linux and MacOS"
            )

        self.policy_bin = Path(os.path.join(f"{script_directory}", f"{DEFAULT_LIB}"))

        if not os.path.exists(self.policy_bin):
            raise RuntimeError("The extension binary file cannot be located.")

    def get_policy_image_layers(
        self, image: str, tag: str, tar_location: str = ""
    ) -> List[str]:
        policy_bin_str = str(self.policy_bin)

        img = image + ":" + tag

        arg_list = [
            f"{policy_bin_str}",
        ]

        # decide if we're reading from a tarball or not
        if tar_location:
            arg_list += ["--tarball", tar_location]
        else:
            arg_list += ["-d"]

        # add the image to the end of the parameter list
        arg_list += ["roothash", "-i", f"{img}"]

        outputlines = None
        err = None

        with subprocess.Popen(
            arg_list,
            executable=policy_bin_str,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ) as layers:
            outputlines, err = layers.communicate()

        output = []
        if outputlines is None:
            eprint("Null pointer detected.")
        elif len(outputlines) > 0:
            output = outputlines.decode("utf8").rstrip("\n").split("\n")
            output = [output[j * 2 + 1] for j in range(len(output) // 2)]
            output = [i.rstrip("\n").split(": ", 1)[1] for i in output]
        else:
            eprint(
                "Cannot get layer hashes. Please check whether the image exists in local repository/daemon."
            )

        if err.decode("utf8") != "":
            eprint(err.decode("utf8"))

        return output
