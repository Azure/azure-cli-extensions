# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This file is a reduced version of qdk-python\azure-quantum\azure\quantum\storage.py
# It only contains the functions required to do inputData blob upload for job submission.
# Other cosmetic changes were made to appease the Azure CLI CI/CD checks.

# Unused imports were removed to reduce Pylint style-rule violations.
import logging
from datetime import datetime, timedelta
from typing import Any
from azure.storage.blob import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
    BlobSasPermissions,
    ContentSettings,
    generate_blob_sas,
)

logger = logging.getLogger(__name__)


def create_container(
    connection_string: str, container_name: str
) -> ContainerClient:
    """
    Creates and initialize a container; returns the client needed to access it.
    """
    blob_service_client = BlobServiceClient.from_connection_string(
        connection_string
    )
    logger.info(
        f'{"Initializing storage client for account:"}'
        + f"{blob_service_client.account_name}"
    )

    container_client = blob_service_client.get_container_client(container_name)
    create_container_using_client(container_client)
    return container_client


def create_container_using_client(container_client: ContainerClient):
    """
    Creates the container if it doesn't already exist.
    """
    if not container_client.exists():
        logger.debug(
            "  - uploading to **new** container: %s",
            container_client.container_name
        )
        container_client.create_container()


def upload_blob(
    container: ContainerClient,
    blob_name: str,
    content_type: str,
    content_encoding: str,
    data: Any,
    return_sas_token: bool = True,
) -> str:
    """
    Uploads the given data to a blob record.
    If a blob with the given name already exist, it throws an error.

    Returns a uri with a SAS token to access the newly created blob.
    """
    create_container_using_client(container)
    logger.info(
        f"Uploading blob '{blob_name}'"
        + f"to container '{container.container_name}'"
        + f"on account: '{container.account_name}'"
    )

    content_settings = ContentSettings(
        content_type=content_type, content_encoding=content_encoding
    )

    blob = container.get_blob_client(blob_name)

    blob.upload_blob(data, content_settings=content_settings)
    logger.debug("  - blob '%s' uploaded. generating sas token.", blob_name)

    if return_sas_token:
        uri = get_blob_uri_with_sas_token(blob)
    else:
        uri = remove_sas_token(blob.url)
    logger.debug("  - blob access url: '%s'.", uri)

    return uri


def get_blob_uri_with_sas_token(blob: BlobClient):
    """Returns a URI for the given blob that contains a SAS Token"""
    sas_token = generate_blob_sas(
        blob.account_name,
        blob.container_name,
        blob.blob_name,
        account_key=blob.credential.account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(days=14),
    )

    return blob.url + "?" + sas_token


def remove_sas_token(sas_uri: str) -> str:
    """Removes the SAS Token from the given URI if it contains one"""
    index = sas_uri.find("?")
    if index != -1:
        sas_uri = sas_uri[0:index]

    return sas_uri
