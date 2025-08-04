##
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
##
import logging
from typing import Any, Dict
from azure.core import exceptions
# from azure.storage.blob import (
from ..azure_storage_blob import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
    BlobSasPermissions,
    ContentSettings,
    generate_blob_sas,
    generate_container_sas,
    BlobType,
    BlobProperties
)
from datetime import datetime, timedelta
from enum import Enum

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
            f'{"  - uploading to **new** container:"}'
            f"{container_client.container_name}"
        )
        container_client.create_container()


def get_container_uri(connection_string: str, container_name: str) -> str:
    """
    Creates and initialize a container;
    returns a URI with a SAS read/write token to access it.
    """
    container = create_container(connection_string, container_name)
    logger.info(
        f'{"Creating SAS token for container"}'
        + f"'{container_name}' on account: '{container.account_name}'"
    )

    sas_token = generate_container_sas(
        container.account_name,
        container.container_name,
        account_key=container.credential.account_key,
        permission=BlobSasPermissions(
            read=True, add=True, write=True, create=True
        ),
        expiry=datetime.utcnow() + timedelta(days=14),
    )

    uri = container.url + "?" + sas_token
    logger.debug(f"  - container url: '{uri}'.")
    return uri


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
    logger.debug(f"  - blob '{blob_name}' uploaded. generating sas token.")

    if return_sas_token:
        uri = get_blob_uri_with_sas_token(blob)
    else:
        uri = remove_sas_token(blob.url)
    logger.debug(f"  - blob access url: '{uri}'.")

    return uri


def append_blob(
    container: ContainerClient,
    blob_name: str,
    content_type: str,
    content_encoding: str,
    data: Any,
    return_sas_token: bool = True,
    metadata: Dict[str, str] = None,
) -> str:
    """
    Uploads the given data to a blob record.
    If a blob with the given name already exist, it throws an error.

    Returns a uri with a SAS token to access the newly created blob.
    """
    create_container_using_client(container)
    logger.info(
        f"Appending data to blob '{blob_name}'"
        + f"in container '{container.container_name}'"
        + f"on account: '{container.account_name}'"
    )

    content_settings = ContentSettings(
        content_type=content_type, content_encoding=content_encoding
    )
    blob = container.get_blob_client(blob_name)
    try:
        props = blob.get_blob_properties()
        if props.blob_type != BlobType.AppendBlob:
            raise Exception("blob must be an append blob")
    except exceptions.ResourceNotFoundError:
        props = blob.create_append_blob(
            content_settings=content_settings, metadata=metadata
        )

    blob.append_block(data, len(data))
    logger.debug(f"  - blob '{blob_name}' appended. generating sas token.")

    if return_sas_token:
        uri = get_blob_uri_with_sas_token(blob)
    else:
        uri = remove_sas_token(blob.url)

    logger.debug(f"  - blob access url: '{uri}'.")

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


def download_blob(blob_url: str) -> Any:
    """
    Downloads the given blob from the container.
    """
    blob_client = BlobClient.from_blob_url(blob_url)
    logger.info(
        f"Downloading blob '{blob_client.blob_name}'"
        + f"from container '{blob_client.container_name}'"
        + f"on account: '{blob_client.account_name}'"
    )

    response = blob_client.download_blob().readall()
    logger.debug(response)

    return response


def download_blob_properties(blob_url: str) -> BlobProperties:
    """Downloads the blob properties from Azure for the given blob URI"""
    blob_client = BlobClient.from_blob_url(blob_url)
    logger.info(
        f"Downloading blob properties '{blob_client.blob_name}'"
        + f"from container '{blob_client.container_name}'"
        + f"on account: '{blob_client.account_name}'"
    )

    response = blob_client.get_blob_properties()
    logger.debug(response)

    return response


def download_blob_metadata(blob_url: str) -> Dict[str, str]:
    """Downloads the blob metadata from the
    blob properties in Azure for the given blob URI"""
    return download_blob_properties(blob_url).metadata


def set_blob_metadata(blob_url: str, metadata: Dict[str, str]):
    """Sets the provided dictionary as the metadata on the Azure blob"""
    blob_client = BlobClient.from_blob_url(blob_url)
    logger.info(
        f"Setting blob properties '{blob_client.blob_name}'"
        + f"from container '{blob_client.container_name}' on account:"
        + f"'{blob_client.account_name}'"
    )
    return blob_client.set_blob_metadata(metadata=metadata)


def remove_sas_token(sas_uri: str) -> str:
    """Removes the SAS Token from the given URI if it contains one"""
    index = sas_uri.find("?")
    if index != -1:
        sas_uri = sas_uri[0:index]

    return sas_uri


def init_blob_for_streaming_upload(
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
        f"Streaming blob '{blob_name}'"
        + f"to container '{container.container_name}' on account:"
        + f"'{container.account_name}'"
    )

    content_settings = ContentSettings(
        content_type=content_type, content_encoding=content_encoding
    )
    blob = container.get_blob_client(blob_name)
    blob.stage_block()
    blob.commit_block_list()
    blob.upload_blob(data, content_settings=content_settings)
    logger.debug(f"  - blob '{blob_name}' uploaded. generating sas token.")

    if return_sas_token:
        sas_token = generate_blob_sas(
            blob.account_name,
            blob.container_name,
            blob.blob_name,
            account_key=blob.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(days=14),
        )

        uri = blob.url + "?" + sas_token
    else:
        uri = remove_sas_token(blob.url)

    logger.debug(f"  - blob access url: '{uri}'.")

    return uri


class StreamedBlobState(str, Enum):
    not_initialized = 0
    uploading = 1
    committed = 2


class StreamedBlob:
    """Class that provides a state machine for writing
    blobs using the Azure Block Blob API

    Internally implements a state machine for uploading blob data.
    To use, start calling `upload_data()`
    to add data blocks. Each call to `upload_data()`
    will synchronously upload an individual block to Azure.
    Once all blocks have been added, call `commit()`
    to commit the blocks and make the blob available/readable.

    :param container: The container client that the blob will be uploaded to
    :param blob_name: The name of the blob
        (including optional path) within the blob container
    :param content_type: The HTTP content type to apply to the blob metadata
    :param content_encoding: The HTTP
        content encoding to apply to the blob metadata
    """

    def __init__(
        self,
        container: ContainerClient,
        blob_name: str,
        content_type: str,
        content_encoding: str,
    ):
        self.container = container
        self.blob_name = blob_name
        self.content_settings = ContentSettings(
            content_type=content_type, content_encoding=content_encoding
        )
        self.state = StreamedBlobState.not_initialized
        self.blob = container.get_blob_client(blob_name)
        self.blocks = []

    def upload_data(self, data):
        """Synchronously uploads a block to the given block blob in Azure

        :param data: The data to be uploaded as a block.
        :type data: Union[Iterable[AnyStr], IO[AnyStr]]
        """
        if self.state == StreamedBlobState.not_initialized:
            create_container_using_client(self.container)
            logger.info(
                f"Streaming blob '{self.blob_name}' to container"
                + f"'{self.container.container_name}'"
                + f"on account: '{self.container.account_name}'"
            )
            self.initialized = True

        self.state = StreamedBlobState.uploading
        id = self._get_next_block_id()
        logger.debug(f"Uploading block '{id}' to {self.blob_name}")
        self.blob.stage_block(id, data, length=len(data))
        self.blocks.append(id)

    def commit(self, metadata: Dict[str, str] = None):
        """Synchronously commits all previously
        uploaded blobs to the block blob

        :param metadata: Optional dictionary of
               metadata to be applied to the block blob
        """
        if self.state == StreamedBlobState.not_initialized:
            raise Exception("StreamedBlob cannot commit before uploading data")
        elif self.state == StreamedBlobState.committed:
            raise Exception("StreamedBlob is already committed")

        logger.debug(f"Committing {len(self.blocks)} blocks {self.blob_name}")
        self.blob.commit_block_list(
            self.blocks,
            content_settings=self.content_settings,
            metadata=metadata,
        )
        self.state = StreamedBlobState.committed
        logger.debug(f"Committed {self.blob_name}")

    def getUri(self, with_sas_token: bool = False):
        """Gets the full Azure Storage URI for the
        uploaded blob after it has been committed"""
        if self.state != StreamedBlobState.committed:
            raise Exception("Can only retrieve sas token for committed blob")
        if with_sas_token:
            return get_blob_uri_with_sas_token(self.blob)

        return remove_sas_token(self.blob.url)

    def _get_next_block_id(self):
        return f"{len(self.blocks):10}"
