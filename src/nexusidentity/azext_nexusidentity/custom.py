# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=too-many-statements

import logging

from knack.util import CLIError  # pylint: disable=unused-import
from knack.log import get_logger

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = get_logger(__name__)


def generate_nexus_identity_keys(algorithm=None):

    import os
    import subprocess
    import sys
    import requests
    import json
    import shutil

    # Generate SSH key
    if sys.platform.startswith("win") or sys.platform.startswith("linux"):

        algoToBeUsed = "ed25519-sk"
        key_name = "id_ed25519_sk"

        if algorithm and algorithm == "ecdsa-sk":
            algoToBeUsed = "ecdsa-sk"
            key_name = "id_ecdsa_sk"

        if sys.platform.startswith("win"):
            dir_path = os.path.expanduser("~\\.ssh")
        elif sys.platform.startswith("linux"):
            dir_path = os.path.expanduser("~/.ssh")

        # check if the ssh directory exists or not
        if not os.path.exists(dir_path):
            try:
                # Create the directory
                os.makedirs(dir_path)
            except OSError as e:
                logger.error("Error creating directory: %s", e)
                raise CLIError(f"Error creating directory: {e}") from e

        # Generate ed25519-sk key
        subprocess.run(
            [
                "ssh-keygen",
                "-t",
                algoToBeUsed,
                "-O",
                "resident",
                "-O",
                "verify-required",
                "-C",
                "NexusIdentitySSHKey",
                "-f",
                os.path.join(dir_path, key_name),
            ],
            check=False,
        )

        # read the key from the file
        try:
            # Read public key
            file_path = key_name + ".pub"
            with open(
                os.path.join(dir_path, file_path), "r", encoding="utf-8"
            ) as key_file:
                public_key = key_file.read()
        except FileNotFoundError as e:
            raise CLIError(f"Error reading public key: {e}") from e
        except OSError as e:
            raise CLIError(f"Unexpected error reading public key: {e}") from e

        try:
            # Get access token using Azure CLI
            if sys.platform.startswith("win"):
                az_path = shutil.which("az")
                if not az_path:
                    raise CLIError("Azure CLI (az) not found in system")
                token_result = subprocess.run(
                    [
                        az_path,
                        "account",
                        "get-access-token",
                        "--resource",
                        "https://graph.microsoft.com",
                        "--output",
                        "json",
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )
            else:
                token_result = subprocess.run(
                    [
                        "az",
                        "account",
                        "get-access-token",
                        "--resource",
                        "https://graph.microsoft.com",
                        "--output",
                        "json",
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )
            access_token = json.loads(token_result.stdout)["accessToken"]
        except Exception as e:
            print("Exception to fetch bearer token:", e)
            logger.error("Failed to obtain access token: %s", e)
            raise CLIError(f"Failed to obtain access token: {e}") from e

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        extension_id = "com.nexusidentity.keys"
        graph_base = "https://graph.microsoft.com/v1.0"

        try:
            # Get user info
            user = requests.get(f"{graph_base}/me", headers=headers)
            user.raise_for_status()
            user = user.json()

            # Get extensions
            ext_resp = requests.get(f"{graph_base}/me/extensions", headers=headers)
            ext_resp.raise_for_status()
            ext_resp = ext_resp.json().get("value", [])
            extension_exists = any(ext.get("id") == extension_id for ext in ext_resp)

            if extension_exists:
                # Update extension
                patch_body = {
                    "@odata.type": "microsoft.graph.openTypeExtension",
                    "extensionName": extension_id,
                    "publicKey": public_key,
                }
                requests.patch(
                    f"{graph_base}/me/extensions/{extension_id}",
                    headers=headers,
                    data=json.dumps(patch_body),
                ).raise_for_status()
                print(
                    f"Successfully updated public key to Microsoft Entra Id account "
                    f"{user.get('mail') or user.get('userPrincipalName')}"
                )
            else:
                # Create extension
                post_body = {
                    "@odata.type": "microsoft.graph.openTypeExtension",
                    "extensionName": extension_id,
                    "publicKey": public_key,
                }
                requests.post(
                    f"{graph_base}/me/extensions",
                    headers=headers,
                    data=json.dumps(post_body),
                ).raise_for_status()
                print(
                    f"Successfully uploaded public key to Microsoft Entra Id account "
                    f"{user.get('mail') or user.get('userPrincipalName')}"
                )

        except requests.HTTPError as e:
            logger.error("HTTP error: %s", e)
            raise CLIError(f"HTTP error: {e}") from e
        except Exception as e:
            logger.error("Unexpected error: %s", e)
            raise CLIError(f"Unexpected error: {e}") from e
    else:
        logger.warning(
            "This command is currently supported only on Windows and linux platforms"
        )
