# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError  # pylint: disable=unused-import
from knack.log import get_logger
from subprocess import DEVNULL

import logging
import sys

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = get_logger(__name__)


def generate_nexus_identity_keys() -> None:

    import os
    import subprocess
    import asyncio

    from azure.identity import InteractiveBrowserCredential
    from msgraph import GraphServiceClient
    from msgraph.generated.models.open_type_extension import OpenTypeExtension
    from msgraph.generated.models.extension import Extension
    from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
    from msgraph.generated.models.o_data_errors.o_data_error import ODataError

    try:

        # Generate SSH key
        subprocess.run(['ssh-keygen',
                        '-t',
                        'ed25519-sk',
                        '-O',
                        'resident',
                        '-O',
                        'verify-required',
                        '-f',
                        os.path.expanduser("~\\.ssh\\id_ecdsa_sk")],
                       stdout=DEVNULL, stderr=DEVNULL,
                       check=True)
    except subprocess.CalledProcessError as e:
        logger.error("Error generating SSH key: %s", e)
        sys.exit(1)

    # currently the cryptography library does not support the ed25519-sk key
    # type, so we will read the public key from the file

    try:
        # Read public key
        with open(os.path.expanduser("~/.ssh/id_ecdsa_sk.pub"), "r") as key_file:
            public_key = key_file.read()
    except FileNotFoundError as e:
        raise CLIError(f"Error reading public key: {e}")
    except OSError as e:
        raise CLIError(f"Unexpected error reading public key: {e}")

    try:
        credential = InteractiveBrowserCredential().get_token(
            'https://graph.microsoft.com//.default')
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
