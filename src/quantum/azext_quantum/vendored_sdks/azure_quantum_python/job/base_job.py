##
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
##
import abc
import logging
import uuid

from enum import Enum
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse, parse_qs
from typing import Any, Dict, Optional, TYPE_CHECKING
from azure.storage.blob import BlobClient

from azure.quantum.storage import upload_blob, download_blob, download_blob_properties, ContainerClient
from azure.quantum._client.models import JobDetails
from azure.quantum.job.workspace_item import WorkspaceItem


if TYPE_CHECKING:
    from azure.quantum.workspace import Workspace


logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 300  # Default timeout for waiting for job to complete

class ContentType(str, Enum):
    json = "application/json"
    text_plain = "text/plain"

class BaseJob(WorkspaceItem):
    # Optionally override these to create a Provider-specific Job subclass
    """
    Base job class with methods to create a job from raw blob data,
    upload blob data and download results.

    :param workspace: Workspace instance of the job
    :type workspace: Workspace
    :param details: Item details model,
            contains item ID, name and other details
    :type details: ItemDetails
    """

    @staticmethod
    def create_job_id() -> str:
        """Create a unique id for a new job."""
        return str(uuid.uuid1())

    @property
    def details(self) -> JobDetails:
        """Job details"""
        return self._details

    @details.setter
    def details(self, value: JobDetails):
        self._details = value

    @property
    def container_name(self):
        """Job input/output data container name"""
        return f"job-{self.id}"

    @classmethod
    def from_input_data(
        cls,
        workspace: "Workspace",
        name: str,
        target: str,
        input_data: bytes,
        content_type: ContentType = ContentType.json,
        blob_name: str = "inputData",
        encoding: str = "",
        job_id: str = None,
        container_name: str = None,
        provider_id: str = None,
        input_data_format: str = None,
        output_data_format: str = None,
        input_params: Dict[str, Any] = None,
        session_id: Optional[str] = None,
        **kwargs
    ) -> "BaseJob":
        """Create a new Azure Quantum job based on a raw input_data payload.

        :param workspace: Azure Quantum workspace to submit the input_data to
        :type workspace: Workspace
        :param name: Name of the job
        :type name: str
        :param target: Azure Quantum target
        :type target: str
        :param input_data: Raw input data to submit
        :type input_data: bytes
        :param blob_name: Input data blob name, defaults to "inputData"
        :type blob_name: str
        :param content_type: Content type, e.g. "application/json"
        :type content_type: ContentType
        :param encoding: input_data encoding, e.g. "gzip", defaults to empty string
        :type encoding: str
        :param job_id: Job ID, defaults to None
        :type job_id: str
        :param container_name: Container name, defaults to None
        :type container_name: str
        :param provider_id: Provider ID, defaults to None
        :type provider_id: str
        :param input_data_format: Input data format, defaults to None
        :type input_data_format: str
        :param output_data_format: Output data format, defaults to None
        :type output_data_format: str
        :param input_params: Input parameters, defaults to None
        :type input_params: Dict[str, Any]
        :param input_params: Input params for job
        :type input_params: Dict[str, Any]
        :return: Azure Quantum Job
        :rtype: Job
        """
        # Generate job ID if not specified
        if job_id is None:
            job_id = cls.create_job_id()

        # Create container if it does not yet exist
        container_uri = workspace.get_container_uri(
            job_id=job_id,
            container_name=container_name
        )
        logger.debug(f"Container URI: {container_uri}")

        # Upload data to container
        input_data_uri = cls.upload_input_data(
            container_uri=container_uri,
            input_data=input_data,
            content_type=content_type,
            blob_name=blob_name,
            encoding=encoding,
        )

        # Create and submit job
        return cls.from_storage_uri(
            workspace=workspace,
            job_id=job_id,
            target=target,
            input_data_uri=input_data_uri,
            container_uri=container_uri,
            name=name,
            input_data_format=input_data_format,
            output_data_format=output_data_format,
            provider_id=provider_id,
            input_params=input_params,
            session_id=session_id,
            **kwargs
        )

    @classmethod
    def from_storage_uri(
        cls,
        workspace: "Workspace",
        name: str,
        target: str,
        input_data_uri: str,
        provider_id: str,
        input_data_format: str,
        output_data_format: str,
        container_uri: str = None,
        job_id: str = None,
        input_params: Dict[str, Any] = None,
        submit_job: bool = True,
        session_id: Optional[str] = None,
        **kwargs
    ) -> "BaseJob":
        """Create new Job from URI if input data is already uploaded
        to blob storage

        :param workspace: Azure Quantum workspace to submit the blob to
        :type workspace: Workspace
        :param name: Job name
        :type name: str
        :param target: Azure Quantum target
        :type target: str
        :param input_data_uri: Input data URI
        :type input_data_uri: str
        :param provider_id: Provider ID
        :type provider_id: str
        :param input_data_format: Input data format
        :type input_data_format: str
        :param output_data_format: Output data format
        :type output_data_format: str
        :param container_uri: Container URI, defaults to None
        :type container_uri: str
        :param job_id: Pre-generated job ID, defaults to None
        :type job_id: str
        :param input_params: Input parameters, defaults to None
        :type input_params: Dict[str, Any]
        :param submit_job: If job should be submitted to the service, defaults to True
        :type submit_job: bool
        :return: Job instance
        :rtype: Job
        """
        # Generate job_id, input_params, data formats and provider ID if not specified
        if job_id is None:
            job_id = cls.create_job_id()
        if input_params is None:
            input_params = {}

        # Create container for output data if not specified
        if container_uri is None:
            container_uri = workspace.get_container_uri(job_id=job_id)

        # Create job details and return Job
        details = JobDetails(
            id=job_id,
            name=name,
            container_uri=container_uri,
            input_data_format=input_data_format,
            output_data_format=output_data_format,
            input_data_uri=input_data_uri,
            provider_id=provider_id,
            target=target,
            input_params=input_params,
            session_id=session_id,
            **kwargs
        )
        job = cls(workspace, details, **kwargs)

        logger.info(
            f"Submitting job '{name}'. \
                Using payload from: '{job.details.input_data_uri}'"
        )

        if submit_job:
            logger.debug(f"==> submitting: {job.details}")
            job.submit()

        return job

    @staticmethod
    def upload_input_data(
        container_uri: str,
        input_data: bytes,
        content_type: Optional[ContentType] = ContentType.json,
        blob_name: str = "inputData",
        encoding: str = "",
        return_sas_token: bool = False
    ) -> str:
        """Upload input data file

        :param container_uri: Container URI
        :type container_uri: str
        :param input_data: Input data in binary format
        :type input_data: bytes
        :param content_type: Content type, e.g. "application/json"
        :type content_type: Optional, ContentType
        :param blob_name: Blob name, defaults to "inputData"
        :type blob_name: str
        :param encoding: Encoding, e.g. "gzip", defaults to ""
        :type encoding: str
        :param return_sas_token: Flag to return SAS token as part of URI, defaults to False
        :type return_sas_token: bool
        :return: Uploaded data URI
        :rtype: str
        """
        container_client = ContainerClient.from_container_url(
            container_uri
        )

        uploaded_blob_uri = upload_blob(
            container_client,
            blob_name,
            content_type,
            encoding,
            input_data,
            return_sas_token=return_sas_token
        )
        return uploaded_blob_uri


    def download_data(self, blob_uri: str) -> dict:
        """Download file from blob uri

        :param blob_uri: Blob URI
        :type blob_uri: str
        :return: Payload from blob
        :rtype: dict
        """
        
        blob_uri_with_sas_token = self._get_blob_uri_with_sas_token(blob_uri)
        payload = download_blob(blob_uri_with_sas_token)

        return payload


    def download_blob_properties(self, blob_uri: str):
        """Download Blob properties

        :param blob_uri: Blob URI
        :type blob_uri: str
        :return: Blob properties
        :rtype: dict
        """

        blob_uri_with_sas_token = self._get_blob_uri_with_sas_token(blob_uri)
        return download_blob_properties(blob_uri_with_sas_token)


    def upload_attachment(
        self,
        name: str,
        data: bytes,
        container_uri: str = None,
        **kwargs
    ) -> str:
        """Uploads an attachment to the job's container file. Attachment's are identified by name.
        Uploading to an existing attachment overrides its previous content.

        :param name: Attachment name
        :type name: str
        :param data: Attachment data in binary format
        :type input_data: bytes
        :param container_uri: Container URI, defaults to the job's linked container.
        :type container_uri: str

        :return: Uploaded data URI
        :rtype: str
        """

        # Use Job's default container if not specified
        if container_uri is None:
            container_uri = self.workspace.get_container_uri(job_id=self.id)

        uploaded_blob_uri = self.upload_input_data(
            container_uri = container_uri,
            blob_name = name,
            input_data = data,
            **kwargs
        )
        return uploaded_blob_uri

    def download_attachment(
        self,
        name: str,
        container_uri: str = None
    ):
        """ Downloads an attachment from job's container in Azure Storage. Attachments are blobs of data
            created as part of the Job's execution, or they can be created by uploading directly from Python
            using the upload_attachment method.
            
        :param name: Attachment name
        :type name: str
        :param container_uri: Container URI, defaults to the job's linked container.
        :type container_uri: str

        :return: Attachment data
        :rtype: bytes
        """

        # Use Job's default container if not specified
        if container_uri is None:
            container_uri = self.workspace.get_container_uri(job_id=self.id)
        
        container_client = ContainerClient.from_container_url(container_uri)
        blob_client = container_client.get_blob_client(name)
        response = blob_client.download_blob().readall()
        return response


    def _get_blob_uri_with_sas_token(self, blob_uri: str) -> str:
        """Get Blob URI with SAS-token if one was not specified in blob_uri parameter
        :param blob_uri: Blob URI
        :type blob_uri: str
        :return: Blob URI with SAS-token
        :rtype: str
        """
        url = urlparse(blob_uri)
        query_params = parse_qs(url.query)
        token_expire_query_param = query_params.get("se")

        token_expire_time = None

        if token_expire_query_param is not None:
            token_expire_time_str = token_expire_query_param[0]

            # Since python < 3.11 can not easily parse Z suffixed UTC timestamp and 
            # assuming that the timestamp is always UTC, we replace that suffix with UTC offset.
            token_expire_time = datetime.fromisoformat(
                token_expire_time_str.replace('Z', '+00:00')
            )
            
            # Make an expiration time a little earlier, so there's no case where token is
            # used a second or so before of its expiration.
            token_expire_time = token_expire_time - timedelta(minutes=5)

        current_utc_time = datetime.now(tz=timezone.utc)
        if token_expire_time is None or current_utc_time >= token_expire_time:
            # blob_uri does not contains SAS token or it is expired,
            # get sas url from service
            blob_client = BlobClient.from_blob_url(
                blob_uri
            )
            blob_uri = self.workspace._get_linked_storage_sas_uri(
                blob_client.container_name, blob_client.blob_name
            )

        return blob_uri