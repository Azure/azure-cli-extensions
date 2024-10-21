# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError  # pylint: disable=unused-import
from knack.log import get_logger

import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = get_logger(__name__)


def generate_nexus_identity_keys() -> None:

    import os
    import subprocess
    import asyncio
    import sys

    from azure.identity import AzureCliCredential
    from msgraph import GraphServiceClient
    from msgraph.generated.models.open_type_extension import OpenTypeExtension
    from msgraph.generated.models.extension import Extension
    from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
    from msgraph.generated.models.o_data_errors.o_data_error import ODataError

    # Generate SSH key
    if sys.platform.startswith("win"):

        dir_path = os.path.expanduser("~\\.ssh")

        # check if the ssh directory exists or not
        if not os.path.exists(dir_path):
            try:
                # Create the directory
                os.makedirs(dir_path)
            except OSError as e:
                logger.error("Error creating directory: %s", e)
                raise CLIError(f"Error creating directory: {e}")

        # Generate ed25519-sk key
        subprocess.run(['ssh-keygen',
                        '-t',
                        'ed25519-sk',
                        '-O',
                        'resident',
                        '-O',
                        'verify-required',
                        '-f',
                        os.path.join(dir_path, "id_ed25519_sk")],
                       check=False)

    # read the key from the file
        try:
            # Read public key
            with open(os.path.join(dir_path, "id_ed25519_sk.pub"), "r") as key_file:
                public_key = key_file.read()
        except FileNotFoundError as e:
            raise CLIError(f"Error reading public key: {e}")
        except OSError as e:
            raise CLIError(f"Unexpected error reading public key: {e}")

        try:
            credential = AzureCliCredential()
            scopes = ['https://graph.microsoft.com//.default']
            graph_client = GraphServiceClient(
                credentials=credential, scopes=scopes)

        except ClientAuthenticationError as e:
            logger.error("Authentication failed: %s", e)
            raise CLIError(f"Authentication failed: {e}")
        except Exception as e:
            logger.error("An unexpected error occurred: %s", e)
            raise CLIError(f"An unexpected error occurred: {e}")

        async def me():
            extension_id = "com.nexusidentity.keys"
            extensions = await graph_client.me.extensions.get()

            extension_exists = any(
                extension.id == extension_id for extension in extensions.value)

            try:
                # Update or create extension
                if extension_exists:
                    request_body = Extension(
                        odata_type="microsoft.graph.openTypeExtension",
                        additional_data={
                            "extension_name": extension_id,
                            "publicKey": public_key
                        }
                    )
                    await graph_client.me.extensions.by_extension_id(extension_id).patch(request_body)
                else:
                    request_body = OpenTypeExtension(
                        odata_type="microsoft.graph.openTypeExtension",
                        extension_name=extension_id,
                        additional_data={
                            "publicKey": public_key
                        }
                    )
                    await graph_client.me.extensions.post(request_body)
            except ODataError as e:
                logger.error("Error updating extension: %s", e)
                raise CLIError(f"Error updating extension: {e}")
            except (HttpResponseError) as e:
                logger.error("Failed to update or create extension: %s", e)
                raise CLIError(f"Failed to update or create extension: {e}")

        asyncio.run(me())
    else:
        logger.warning(
            "This command is currently supported only on Windows platforms")
