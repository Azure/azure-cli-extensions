# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import subprocess
import os
import stat
import platform
from typing import List
import requests
from knack.log import get_logger
from azext_confcom.errors import eprint
from azext_confcom.config import (
    REGO_CONTAINER_START,
    REGO_FRAGMENT_START,
    POLICY_FIELD_CONTAINERS,
    POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS,
    POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_ISSUER,
    POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_FEED,
    POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_MINIMUM_SVN,
    ACI_FIELD_CONTAINERS_REGO_FRAGMENTS_INCLUDES,
)

logger = get_logger(__name__)
host_os = platform.system()
machine = platform.machine()


def call_cose_sign_tool(args: List[str], error_message: str, check=False):
    item = subprocess.run(args, check=check, capture_output=True, timeout=120)

    if item.returncode != 0:
        eprint(f"{error_message}: {item.stderr.decode('utf-8')}", exit_code=item.returncode)

    return item


class CoseSignToolProxy:  # pylint: disable=too-few-public-methods

    @staticmethod
    def download_binaries():
        dir_path = os.path.dirname(os.path.realpath(__file__))

        bin_folder = os.path.join(dir_path, "bin")
        if not os.path.exists(bin_folder):
            os.makedirs(bin_folder)

        # get the most recent release artifacts from github
        r = requests.get("https://api.github.com/repos/microsoft/cosesign1go/releases")
        r.raise_for_status()
        needed_assets = ["sign1util", "sign1util.exe"]

        # these should be newest to oldest
        for release in r.json():
            # search for both windows and linux binaries
            needed_asset_info = [asset for asset in release["assets"] if asset["name"] in needed_assets]
            if len(needed_asset_info) == len(needed_assets):
                for asset in needed_asset_info:
                    # get the download url for the dmverity-vhd file
                    exe_url = asset["browser_download_url"]
                    # download the file
                    r = requests.get(exe_url)
                    r.raise_for_status()
                    # save the file to the bin folder
                    with open(os.path.join(bin_folder, asset["name"]), "wb") as f:
                        f.write(r.content)
                # stop iterating through releases
                break

    def __init__(self):
        script_directory = os.path.dirname(os.path.realpath(__file__))
        DEFAULT_LIB = "./bin/sign1util"

        if host_os == "Linux":
            DEFAULT_LIB += ""
        elif host_os == "Windows":
            DEFAULT_LIB += ".exe"
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

    def cose_sign(
        self,
        payload_path: str,
        key_path: str,
        cert_path: str,
        feed: str,
        iss: str,
        algo: str,
        out_path: str = "payload.rego.cose",
    ) -> bool:
        policy_bin_str = str(self.policy_bin)

        arg_list = [
            policy_bin_str,
            "create",
            "-algo",
            algo,
            "-chain",
            cert_path,
            "-claims",
            payload_path,
            "-key",
            key_path,
            "-salt",
            "zero",
            "-content-type",
            "application/unknown+rego",
            "-out",
            out_path,
        ]

        if feed:
            arg_list.extend(["-feed", feed])

        if iss:
            arg_list.extend(["-issuer", iss])
        logger.info("Signing the policy fragment: %s", out_path)
        call_cose_sign_tool(arg_list, "Error signing the policy fragment")
        return True

    def create_issuer(self, cert_path: str) -> str:
        policy_bin_str = str(self.policy_bin)

        arg_list = [policy_bin_str, "did-x509", "-chain", cert_path, "-policy", "CN"]

        item = call_cose_sign_tool(arg_list, "Error creating the issuer")

        return item.stdout.decode("utf-8")

    # generate an import statement from a signed policy fragment
    def generate_import_from_path(self, fragment_path: str, minimum_svn: str) -> str:
        if not os.path.exists(fragment_path):
            eprint(f"The fragment file at {fragment_path} does not exist")

        policy_bin_str = str(self.policy_bin)

        arg_list_chain = [policy_bin_str, "check", "--in", fragment_path, "--verbose"]
        logger.info("Extracting import statement from signed fragment: %s", fragment_path)
        item = call_cose_sign_tool(arg_list_chain, "Error getting information from signed fragment file")

        stdout = item.stdout.decode("utf-8")
        # extract issuer, feed, and payload from the fragment
        issuer = stdout.split("iss: ")[1].split("\n")[0]
        feed = stdout.split("feed: ")[1].split("\n")[0]
        payload = stdout.split("payload:")[1]

        includes = []
        if REGO_CONTAINER_START in payload:
            includes.append(POLICY_FIELD_CONTAINERS)

        if REGO_FRAGMENT_START in payload:
            includes.append(POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS)

        # put it all together
        import_statement = {
            POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_ISSUER: issuer,
            POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_FEED: feed,
            POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_MINIMUM_SVN: minimum_svn,
            ACI_FIELD_CONTAINERS_REGO_FRAGMENTS_INCLUDES: includes,
        }

        return import_statement

    def extract_payload_from_path(self, fragment_path: str) -> str:
        policy_bin_str = str(self.policy_bin)
        if not os.path.exists(fragment_path):
            eprint(f"The fragment file at {fragment_path} does not exist")

        arg_list_chain = [policy_bin_str, "check", "--in", fragment_path, "--verbose"]
        logger.info("Extracting payload from signed fragment: %s", fragment_path)
        item = call_cose_sign_tool(arg_list_chain, "Error getting information from signed fragment file")

        stdout = item.stdout.decode("utf-8")
        return stdout.split("payload:")[1]

    def extract_feed_from_path(self, fragment_path: str) -> str:
        policy_bin_str = str(self.policy_bin)
        if not os.path.exists(fragment_path):
            eprint(f"The fragment file at {fragment_path} does not exist")

        arg_list_chain = [policy_bin_str, "check", "--in", fragment_path, "--verbose"]
        logger.info("Extracting feed from signed fragment: %s", fragment_path)
        item = call_cose_sign_tool(arg_list_chain, "Error getting information from signed fragment file")

        stdout = item.stdout.decode("utf-8")

        # we want the text between the name and the next newline
        return stdout.split("feed: ")[1].split("\n")[0]
