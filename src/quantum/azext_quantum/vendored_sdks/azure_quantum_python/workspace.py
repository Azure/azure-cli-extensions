##
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
##
"""
Module providing the Workspace class, used to connect to
an Azure Quantum Workspace.
"""

from __future__ import annotations
from datetime import datetime
import logging
# from urllib.parse import quote
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    TYPE_CHECKING,
    Tuple,
    Union,
)
from typing_extensions import Self
# from azure.core.paging import ItemPaged
# from azure.quantum._client import WorkspaceClient
from ._client import WorkspaceClient
# from azure.quantum._client.models import JobDetails, ItemDetails, SessionDetails
# from azure.quantum._client.operations._operations import (
from ._client.operations._operations import (
    # ServicesJobsOperations,
    ServicesStorageOperations,
    # ServicesQuotasOperations,
    # ServicesSessionsOperations,
    # ServicesTopLevelItemsOperations
)
# from azure.quantum._client.models import (
from ._client.models import (
    BlobDetails,
    # JobStatus,
    # TargetStatus,
)
# from azure.quantum import Job, Session
# from azure.quantum.job.workspace_item_factory import WorkspaceItemFactory
# from azure.quantum._workspace_connection_params import (
from ._workspace_connection_params import (
    WorkspaceConnectionParams
)
# from azure.quantum._constants import (
from ._constants import (
    ConnectionConstants,
)
# from azure.quantum.storage import (
from .storage import (
    get_container_uri,
)
# from azure.quantum._mgmt_client import WorkspaceMgmtClient
from ._mgmt_client import WorkspaceMgmtClient
# if TYPE_CHECKING:
#     from azure.quantum.target import Target

logger = logging.getLogger(__name__)

__all__ = ["Workspace"]

# pylint: disable=line-too-long
# pylint: disable=too-many-public-methods
class Workspace:
    """
    Represents an Azure Quantum workspace.

    When creating a Workspace object, callers have several options for
    identifying the Azure Quantum workspace (in order of precedence):
    1. specify a valid resource ID; or
    2. specify a valid subscription ID, resource group, and workspace name; or
    3. specify a valid workspace name.

    You can also use a connection string to specify the connection parameters
    to an Azure Quantum Workspace by calling
    :obj:`~ Workspace.from_connection_string() <Workspace.from_connection_string>`.

    If the Azure Quantum workspace does not have linked storage, the caller
    must also pass a valid Azure storage account connection string.

    :param subscription_id:
        The Azure subscription ID.
        Ignored if resource_id is specified.

    :param resource_group:
        The Azure resource group name.
        Ignored if resource_id is specified.

    :param name:
        The Azure Quantum workspace name.
        Ignored if resource_id is specified.

    :param storage:
        The Azure storage account connection string.
        Required only if the specified Azure Quantum
        workspace does not have linked storage.

    :param resource_id:
        The resource ID of the Azure Quantum workspace.

    :param location:
        The Azure region where the Azure Quantum workspace is provisioned.
        This may be specified as a region name such as
        \"East US\" or a location name such as \"eastus\".

    :param credential:
        The credential to use to connect to Azure services.
        Normally one of the credential types from [Azure.Identity](https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes).

        Defaults to \"DefaultAzureCredential\", which will attempt multiple
        forms of authentication.

    :param user_agent:
        Add the specified value as a prefix to the HTTP User-Agent header
        when communicating to the Azure Quantum service.
    """
    
    # Internal parameter names
    _FROM_CONNECTION_STRING_PARAM = '_from_connection_string'
    _QUANTUM_ENDPOINT_PARAM = '_quantum_endpoint'
    _WORKSPACE_KIND_PARAM = '_workspace_kind'
    _MGMT_CLIENT_PARAM = '_mgmt_client'
    
    def __init__(
        self,
        subscription_id: Optional[str] = None,
        resource_group: Optional[str] = None,
        name: Optional[str] = None,
        storage: Optional[str] = None,
        resource_id: Optional[str] = None,
        location: Optional[str] = None,
        credential: Optional[object] = None,
        user_agent: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        # Extract internal params before passing kwargs to WorkspaceConnectionParams
        # Param to track whether the workspace was created from a connection string
        from_connection_string = kwargs.pop(Workspace._FROM_CONNECTION_STRING_PARAM, False)
        # In case from connection string, quantum_endpoint must be passed
        quantum_endpoint = kwargs.pop(Workspace._QUANTUM_ENDPOINT_PARAM, None)
        workspace_kind = kwargs.pop(Workspace._WORKSPACE_KIND_PARAM, None)
        # Params to pass a mock in tests
        self._mgmt_client = kwargs.pop(Workspace._MGMT_CLIENT_PARAM, None)
        
        connection_params = WorkspaceConnectionParams(
            location=location,
            subscription_id=subscription_id,
            resource_group=resource_group,
            workspace_name=name,
            credential=credential,
            resource_id=resource_id,
            quantum_endpoint=quantum_endpoint,
            user_agent=user_agent,
            workspace_kind=workspace_kind,
            **kwargs
        ).default_from_env_vars()

        logger.info("Using %s environment.", connection_params.environment)

        connection_params.assert_have_enough_for_discovery()

        connection_params.on_new_client_request = self._on_new_client_request

        self._connection_params = connection_params
        self._storage = storage

        if not self._mgmt_client:
            credential = connection_params.get_credential_or_default()
            self._mgmt_client = WorkspaceMgmtClient(
                credential=credential, 
                base_url=connection_params.arm_endpoint, 
                user_agent=connection_params.get_full_user_agent(),
            )
        
        # pylint: disable=protected-access
        using_connection_string = (
            from_connection_string
            or connection_params._used_connection_string
        )

        # Populate workspace details from ARG if not using connection string and 
        # name is provided but missing subscription and/or resource group
        if not using_connection_string \
           and not connection_params.can_build_resource_id():
            self._mgmt_client.load_workspace_from_arg(connection_params)

        # Populate workspace details from ARM if not using connection string and not loaded from ARG
        if not using_connection_string and not connection_params.is_complete():
            self._mgmt_client.load_workspace_from_arm(connection_params)
        
        connection_params.assert_complete()

        # Create WorkspaceClient
        self._client = self._create_client()

    def _on_new_client_request(self) -> None:
        """
        An internal callback method used by the WorkspaceConnectionParams
        to ask the Workspace to recreate the underlying Azure SDK REST API client.
        This is used when some value (such as the UserAgent) has changed
        in the WorkspaceConnectionParams and requires the client to be
        recreated.
        """
        self._client = self._create_client()

    # @property
    # def location(self) -> str:
    #     """
    #     Returns the Azure location of the Quantum Workspace.

    #     :return: Azure location name.
    #     :rtype: str
    #     """
    #     return self._connection_params.location

    @property
    def subscription_id(self) -> str:
        """
        Returns the Azure Subscription ID of the Quantum Workspace.

        :return: Azure Subscription ID.
        :rtype: str
        """
        return self._connection_params.subscription_id

    @property
    def resource_group(self) -> str:
        """
        Returns the Azure Resource Group of the Quantum Workspace.

        :return: Azure Resource Group name.
        :rtype: str
        """
        return self._connection_params.resource_group

    @property
    def name(self) -> str:
        """
        Returns the Name of the Quantum Workspace.

        :return: Azure Quantum Workspace name.
        :rtype: str
        """
        return self._connection_params.workspace_name

    # @property
    # def credential(self) -> Any:
    #     """
    #     Returns the Credential used to connect to the Quantum Workspace.

    #     :return: Azure SDK Credential from [Azure.Identity](https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes).
    #     :rtype: typing.Any
    #     """
    #     return self._connection_params.credential

    @property
    def storage(self) -> str:
        """
        Returns the Azure Storage account name associated with the Quantum Workspace.

        :return: Azure Storage account name.
        :rtype: str
        """
        return self._storage

    def _create_client(self) -> WorkspaceClient:
        """"
        An internal method to (re)create the underlying Azure SDK REST API client.

        :return: Azure SDK REST API client for Azure Quantum.
        :rtype: WorkspaceClient
        """
        connection_params = self._connection_params
        kwargs = {}
        if connection_params.api_version:
            kwargs["api_version"] = connection_params.api_version
        client = WorkspaceClient(
            region=connection_params.location,
            credential=connection_params.get_credential_or_default(),
            subscription_id=connection_params.subscription_id,
            resource_group_name=connection_params.resource_group,
            workspace_name=connection_params.workspace_name,
            user_agent=connection_params.get_full_user_agent(),
            credential_scopes = [ConnectionConstants.DATA_PLANE_CREDENTIAL_SCOPE],
            endpoint=connection_params.quantum_endpoint,
            authentication_policy=connection_params.get_auth_policy(),
            **kwargs
        )
        return client

    # @property
    # def user_agent(self) -> str:
    #     """
    #     Returns the Workspace's UserAgent string that is sent to
    #     the service via the UserAgent header.

    #     :return: User Agent string.
    #     :rtype: str
    #     """
    #     return self._connection_params.get_full_user_agent()

    # def append_user_agent(self, value: str) -> None:
    #     """
    #     Append a new value to the Workspace's UserAgent.
    #     The values are appended using a dash.

    #     :param value:
    #         UserAgent value to add, e.g. "azure-quantum-<plugin>"
    #     """
    #     self._connection_params.append_user_agent(value=value)

    # @classmethod
    # def from_connection_string(cls, connection_string: str, **kwargs) -> Workspace:
    #     """
    #     Creates a new Azure Quantum Workspace client from a connection string.

    #     :param connection_string:
    #         A valid connection string, usually obtained from the
    #         `Quantum Workspace -> Operations -> Access Keys` blade in the Azure Portal.

    #     :return: New Azure Quantum Workspace client.
    #     :rtype: Workspace
    #     """
    #     connection_params = WorkspaceConnectionParams(connection_string=connection_string)
    #     kwargs[cls._FROM_CONNECTION_STRING_PARAM] = True
    #     kwargs[cls._QUANTUM_ENDPOINT_PARAM] = connection_params.quantum_endpoint
    #     kwargs[cls._WORKSPACE_KIND_PARAM] = connection_params.workspace_kind.value if connection_params.workspace_kind else None
    #     return cls(
    #         subscription_id=connection_params.subscription_id,
    #         resource_group=connection_params.resource_group,
    #         name=connection_params.workspace_name,
    #         location=connection_params.location,
    #         credential=connection_params.get_credential_or_default(),
    #         **kwargs)

    # def _get_top_level_items_client(self) -> ServicesTopLevelItemsOperations:
    #     """
    #     Returns the internal Azure SDK REST API client
    #     for the `{workspace}/topLevelItems` API.

    #     :return: REST API client for the `topLevelItems` API.
    #     :rtype: ServicesTopLevelItemsOperations
    #     """
    #     return self._client.services.top_level_items

    # def _get_sessions_client(self) -> ServicesSessionsOperations:
    #     """
    #     Returns the internal Azure SDK REST API client
    #     for the `{workspace}/sessions` API.

    #     :return: REST API client for the `sessions` API.
    #     :rtype: ServicesSessionsOperations
    #     """
    #     return self._client.services.sessions

    # def _get_jobs_client(self) -> ServicesJobsOperations:
    #     """
    #     Returns the internal Azure SDK REST API client
    #     for the `{workspace}/jobs` API.

    #     :return: REST API client for the `jobs` API.
    #     :rtype: ServicesJobsOperations
    #     """
    #     return self._client.services.jobs

    def _get_workspace_storage_client(self) -> ServicesStorageOperations:
        """
        Returns the internal Azure SDK REST API client
        for the `{workspace}/storage` API.

        :return: REST API client for the `storage` API.
        :rtype: ServicesStorageOperations
        """
        return self._client.services.storage

    # def _get_quotas_client(self) -> ServicesQuotasOperations:
    #     """
    #     Returns the internal Azure SDK REST API client
    #     for the `{workspace}/quotas` API.

    #     :return: REST API client for the `quotas` API.
    #     :rtype: ServicesQuotasOperations
    #     """
    #     return self._client.services.quotas

    def _get_linked_storage_sas_uri(
        self,
        container_name: str,
        blob_name: Optional[str] = None
    ) -> str:
        """
        Calls the service and returns a container/blob SAS URL
        for the Storage associated with the Quantum Workspace.

        :param container_name:
            The name of the storage container.

        :param blob_name:
            Optional name of the blob. Defaults to `None`.

        :return: Storage Account SAS URL to a container or blob.
        :rtype: str
        """
        client = self._get_workspace_storage_client()
        blob_details = BlobDetails(
            container_name=container_name, blob_name=blob_name
        )
        container_uri = client.get_sas_uri(
            self.subscription_id,
            self.resource_group,
            self.name, 
            blob_details=blob_details)

        logger.debug("Container URI from service: %s", container_uri)
        return container_uri.sas_uri

    # def submit_job(self, job: Job) -> Job:
    #     """
    #     Submits a job to be processed in the Workspace.

    #     :param job:
    #         Job to submit.

    #     :return: Azure Quantum Job that was submitted, with an updated status.
    #     :rtype: Job
    #     """
    #     client = self._get_jobs_client()
    #     details = client.create(
    #         self.subscription_id,
    #         self.resource_group,
    #         self.name,
    #         job.details.id, 
    #         job.details
    #     )
    #     return Job(self, details)

    # def cancel_job(self, job: Job) -> Job:
    #     """
    #     Requests the Workspace to cancel the
    #     execution of a job.

    #     :param job:
    #         Job to cancel.

    #     :return: Azure Quantum Job that was requested to be cancelled, with an updated status.
    #     :rtype: Job
    #     """
    #     client = self._get_jobs_client()
    #     client.delete(
    #         self.subscription_id,
    #         self.resource_group,
    #         self.name,
    #         job.details.id)
    #     details = client.get(
    #         self.subscription_id,
    #         self.resource_group,
    #         self.name,
    #         job.id)
    #     return Job(self, details)

    # def get_job(self, job_id: str) -> Job:
    #     """
    #     Returns the job corresponding to the given id.
        
    #     :param job_id:
    #         Id of a job to fetch.

    #     :return: Azure Quantum Job.
    #     :rtype: Job
    #     """
    #     # pylint: disable=import-outside-toplevel
    #     from azure.quantum.target.target_factory import TargetFactory
    #     from azure.quantum.target import Target

    #     client = self._get_jobs_client()
    #     details = client.get(
    #         self.subscription_id,
    #         self.resource_group,
    #         self.name,
    #         job_id)
    #     target_factory = TargetFactory(base_cls=Target, workspace=self)
    #     # pylint: disable=protected-access
    #     target_cls = target_factory._target_cls(
    #         details.provider_id,
    #         details.target)
    #     job_cls = target_cls._get_job_class()
    #     return job_cls(self, details)

    # def list_jobs(
    #     self,
    #     name_match: Optional[str] = None,
    #     job_type: Optional[list[str]]= None,
    #     provider: Optional[list[str]]= None,
    #     target: Optional[list[str]]= None,
    #     status: Optional[list[JobStatus]] = None,
    #     created_after: Optional[datetime] = None,
    #     created_before: Optional[datetime] = None,
    #     orderby_property: Optional[str] = None,
    #     is_asc: Optional[bool] = True
    # ) -> List[Job]:
    #     """
    #     Returns list of jobs that meet optional (limited) filter criteria.

    #     :param name_match:
    #         Optional Regular Expression for job name matching. Defaults to `None`.

    #     :param status:
    #         Optional filter by job status. Defaults to `None`.

    #     :param created_after:
    #         Optional filter by jobs that were created after the given time. Defaults to `None`.

    #     :return: Jobs that matched the search criteria.
    #     :rtype: typing.List[Job]
    #     """
    #     paginator = self.list_jobs_paginated (
    #         name_match=name_match,
    #         job_type=job_type,
    #         provider=provider,
    #         target=target,
    #         status=status,
    #         created_after=created_after,
    #         created_before=created_before,
    #         orderby_property=orderby_property,
    #         is_asc=is_asc)

    #     result = []
    #     for j in paginator:
    #         deserialized_job = Job(self, j)
    #         result.append(deserialized_job)

    #     return result

    # def list_jobs_paginated( 
    #     self,
    #     *,
    #     name_match: Optional[str] = None, 
    #     job_type: Optional[str]= None, 
    #     provider: Optional[list[str]]= None, 
    #     target: Optional[list[str]]= None, 
    #     status: Optional[list[JobStatus]] = None, 
    #     created_after: Optional[datetime] = None,
    #     created_before: Optional[datetime] = None, 
    #     skip: Optional[int] = 0,
    #     top: Optional[int]=100,
    #     orderby_property: Optional[str] = None,
    #     is_asc: Optional[bool] = True
    # ) -> ItemPaged[JobDetails]:
    #     client = self._get_jobs_client()

    #     job_filter = self._create_filter(
    #         job_name=name_match,
    #         job_type=job_type,
    #         provider_ids=provider,
    #         target=target,
    #         status=status,
    #         created_after=created_after,
    #         created_before=created_before
    #     )
    #     orderby = self._create_orderby(orderby_property, is_asc)

    #     return client.list(subscription_id=self.subscription_id, resource_group_name=self.resource_group, workspace_name=self.name, filter=job_filter, orderby=orderby, top = top, skip = skip)

    # def _get_target_status(
    #         self,
    #         name: Optional[str] = None,
    #         provider_id: Optional[str] = None,
    #     ) -> List[Tuple[str, TargetStatus]]:
    #     """
    #     Returns a list of tuples containing the `Provider ID` and `Target Status`,
    #     with the option of filtering that list by a combination of Provider ID and Target Name.

    #     :param name:
    #         Optional name of the Target to filter for. Defaults to `None`.

    #     :param provider_id:
    #         Optional Provider ID to filter for. Defaults to `None`.

    #     :return: List of tuples containing Provider ID and TargetStatus.
    #     :rtype: typing.List[typing.Tuple[str, TargetStatus]]
    #     """
    #     return [
    #         (provider.id, target)
    #         for provider in self._client.services.providers.list(
    #             self.subscription_id,
    #             self.resource_group,
    #             self.name)
    #         for target in provider.targets
    #         if (provider_id is None or provider.id.lower() == provider_id.lower())
    #             and (name is None or target.id.lower() == name.lower())
    #     ]

    # def get_targets(
    #     self,
    #     name: Optional[str] = None,
    #     provider_id: Optional[str] = None,
    # ) -> Union[Target, Iterable[Target]]:
    #     """
    #     Returns all available targets for this workspace filtered by Target name and Provider ID.
    #     If the target name is passed, a single `Target` object will be returned.
    #     Otherwise it returns a iterable/list of `Target` objects, optionally filtered by the Provider ID.

    #     :param name:
    #         Optional target name to filter by, defaults to `None`.
        
    #     :param provider_id:
    #         Optional provider Id to filter by, defaults to `None`.

    #     :return: A single Azure Quantum Target or a iterable/list of Targets.
    #     :rtype: typing.Union[Target, typing.Iterable[Target]]
    #     """
    #     # pylint: disable=import-outside-toplevel
    #     from azure.quantum.target.target_factory import TargetFactory
    #     from azure.quantum.target import Target

    #     target_factory = TargetFactory(
    #         base_cls=Target,
    #         workspace=self
    #     )
    #     return target_factory.get_targets(
    #         name=name,
    #         provider_id=provider_id
    #     )

    # def get_quotas(self) -> List[Dict[str, Any]]:
    #     """
    #     Get a list of quotas for the given workspace.
    #     Each quota is represented as a dictionary, containing the
    #     properties for that quota.

    #     Common Quota properties are:
    #     - "dimension": The dimension that the quota is applied to. 
    #     - "scope": The scope that the quota is applied to.
    #     - "provider_id": The provider that the quota is applied to.
    #     - "utilization": The current utilization of the quota.
    #     - "limit": The limit of the quota.
    #     - "period": The period that the quota is applied to.

    #     :return: Workspace quotas.
    #     :rtype: typing.List[typing.Dict[str, typing.Any]
    #     """
    #     client = self._get_quotas_client()
    #     return [q.as_dict() for q in client.list(
    #         self.subscription_id,
    #         self.resource_group,
    #         self.name
    #     )]

    # def list_top_level_items(
    #     self,
    #     name_match: Optional[str] = None,
    #     item_type: Optional[list[str]]= None,
    #     job_type: Optional[list[str]]= None,
    #     provider: Optional[list[str]]= None,
    #     target: Optional[list[str]]= None,
    #     status: Optional[list[JobStatus]] = None,
    #     created_after: Optional[datetime] = None,
    #     created_before: Optional[datetime] = None,
    #     orderby_property: Optional[str] = None,
    #     is_asc: Optional[bool] = True
    # ) -> List[Union[Job, Session]]:
    #     """
    #     Get a list of top level items for the given workspace,
    #     which can be standalone Jobs (Jobs not associated with a Session)
    #     or Sessions (which can contain Jobs).

    #     :return: List of Workspace top level Jobs or Sessions.
    #     :rtype: typing.List[typing.Union[Job, Session]]
    #     """
    #     paginator = self.list_top_level_items_paginated(
    #         name_match=name_match,
    #         item_type=item_type,
    #         job_type=job_type,
    #         provider=provider,
    #         target=target,
    #         status=status,
    #         created_after=created_after,
    #         created_before=created_before,
    #         orderby_property=orderby_property,
    #         is_asc=is_asc
    #     )

    #     result = [WorkspaceItemFactory.__new__(workspace=self, item_details=item_details)
    #               for item_details in paginator]
    #     return result

    # def list_top_level_items_paginated( 
    #     self,
    #     *,
    #     name_match: Optional[str] = None, 
    #     item_type: Optional[str]= None, 
    #     job_type: Optional[str]= None, 
    #     provider: Optional[list[str]]= None, 
    #     target: Optional[list[str]]= None, 
    #     status: Optional[list[JobStatus]] = None, 
    #     created_after: Optional[datetime] = None,
    #     created_before: Optional[datetime] = None, 
    #     skip: Optional[int] = 0,
    #     top: Optional[int]=100,
    #     orderby_property: Optional[str] = None,
    #     is_asc: Optional[bool] = True
    # ) -> ItemPaged[ItemDetails]:
    #     client = self._get_top_level_items_client()

    #     top_level_item_filter = self._create_filter(
    #         job_name=name_match,
    #         item_type=item_type,
    #         job_type=job_type,
    #         provider_ids=provider,
    #         target=target,
    #         status=status,
    #         created_after=created_after,
    #         created_before=created_before
    #     )
    #     orderby = self._create_orderby(orderby_property, is_asc)

    #     return client.listv2(subscription_id=self.subscription_id, resource_group_name=self.resource_group, workspace_name=self.name, filter=top_level_item_filter, orderby=orderby, top = top, skip = skip)

    # def list_sessions(
    #     self,
    #     provider: Optional[list[str]]= None,
    #     target: Optional[list[str]]= None,
    #     status: Optional[list[JobStatus]] = None,
    #     created_after: Optional[datetime] = None,
    #     created_before: Optional[datetime] = None,
    #     orderby_property: Optional[str] = None,
    #     is_asc: Optional[bool] = True
    # ) -> List[Session]:
    #     """
    #     Get the list of sessions in the given workspace.

    #     :return: List of Workspace Sessions.
    #     :rtype: typing.List[Session]
    #     """
    #     paginator = self.list_sessions_paginated(
    #         provider=provider,
    #         target=target,
    #         status=status,
    #         created_after=created_after,
    #         created_before=created_before,
    #         orderby_property=orderby_property,
    #         is_asc=is_asc)

    #     result = [Session(workspace=self,details=session_details)
    #               for session_details in paginator]
    #     return result
    
    # def list_sessions_paginated(
    #     self,
    #     *,
    #     provider: Optional[list[str]]= None, 
    #     target: Optional[list[str]]= None, 
    #     status: Optional[list[JobStatus]] = None, 
    #     created_after: Optional[datetime] = None,
    #     created_before: Optional[datetime] = None, 
    #     skip: Optional[int] = 0, 
    #     top: Optional[int]=100, 
    #     orderby_property: Optional[str] = None,
    #     is_asc: Optional[bool] = True
    # ) -> ItemPaged[SessionDetails]:
    #     """
    #     Get the list of sessions in the given workspace.

    #     :return: List of Workspace Sessions.
    #     :rtype: typing.List[Session]
    #     """
    #     client = self._get_sessions_client()
    #     session_filter = self._create_filter(
    #         provider_ids=provider,
    #         target=target,
    #         status=status,
    #         created_after=created_after,
    #         created_before=created_before
    #     )

    #     orderby = self._create_orderby(orderby_property=orderby_property, is_asc=is_asc)

    #     return client.listv2(subscription_id=self.subscription_id, resource_group_name=self.resource_group, workspace_name=self.name, filter = session_filter, orderby=orderby, skip=skip, top=top)

    # def open_session(
    #     self,
    #     session: Session,
    # ) -> None:
    #     """
    #     Opens/creates a session in the given workspace.

    #     :param session:
    #         The session to be opened/created.

    #     :return: A new open Azure Quantum Session.
    #     :rtype: Session
    #     """
    #     client = self._get_sessions_client()
    #     session.details = client.open(
    #         self.subscription_id,
    #         self.resource_group,
    #         self.name,
    #         session.id,
    #         session.details)

    # def close_session(
    #     self,
    #     session: Session
    # ) -> None:
    #     """
    #     Closes a session in the given workspace if the
    #     session is not in a terminal state.
    #     Otherwise, just refreshes the session details.

    #     :param session:
    #         The session to be closed.
    #     """
    #     client = self._get_sessions_client()
    #     if not session.is_in_terminal_state():
    #         session.details = client.close(
    #             self.subscription_id,
    #             self.resource_group,
    #             self.name,
    #             session_id=session.id)
    #     else:
    #         session.details = client.get(
    #             self.subscription_id,
    #             self.resource_group,
    #             self.name,
    #             session_id=session.id)

    #     if session.target:
    #         if (session.target.latest_session
    #             and session.target.latest_session.id == session.id):
    #             session.target.latest_session.details = session.details

    # def refresh_session(
    #     self,
    #     session: Session
    # ) -> None:
    #     """
    #     Updates the session details with the latest information
    #     from the workspace.

    #     :param session:
    #         The session to be refreshed.
    #     """
    #     session.details = self.get_session(session_id=session.id).details

    # def get_session(
    #     self,
    #     session_id: str
    # ) -> Session:
    #     """
    #     Gets a session from the workspace.

    #     :param session_id:
    #         The id of session to be retrieved.

    #     :return: Azure Quantum Session
    #     :rtype: Session
    #     """
    #     client = self._get_sessions_client()
    #     session_details = client.get(
    #         self.subscription_id,
    #         self.resource_group,
    #         self.name,
    #         session_id=session_id)
    #     result = Session(workspace=self, details=session_details)
    #     return result

    # def list_session_jobs(
    #     self,
    #     session_id: str,
    #     name_match: Optional[str] = None,
    #     status: Optional[list[JobStatus]] = None,
    #     orderby_property: Optional[str] = None,
    #     is_asc: Optional[bool] = True
    # ) -> List[Job]:
    #     """
    #     Gets all jobs associated with a session.

    #     :param session_id:
    #         The id of session.

    #     :return: List of all jobs associated with a session.
    #     :rtype: typing.List[Job]
    #     """
    #     paginator = self.list_session_jobs_paginated(
    #         session_id=session_id,
    #         name_match=name_match,
    #         status=status,
    #         orderby_property=orderby_property,
    #         is_asc=is_asc)

    #     result = [Job(workspace=self, job_details=job_details)
    #               for job_details in paginator]
    #     return result

    # def list_session_jobs_paginated(
    #     self,
    #     *,
    #     session_id: str,
    #     name_match: Optional[str] = None,
    #     status: Optional[list[JobStatus]] = None,
    #     skip: Optional[int] = 0,
    #     top: Optional[int]=100,
    #     orderby_property: Optional[str] = None,
    #     is_asc: Optional[bool] = True
    # ) -> ItemPaged[JobDetails]:
    #     """
    #     Gets all jobs associated with a session.

    #     :param session_id:
    #         The id of session.

    #     :return: List of all jobs associated with a session.
    #     :rtype: typing.List[Job]
    #     """
    #     client = self._get_sessions_client()

    #     session_job_filter = self._create_filter(
    #         job_name=name_match,
    #         status=status
    #     )

    #     orderby = self._create_orderby(orderby_property=orderby_property, is_asc=is_asc)

    #     return client.jobs_list(subscription_id=self.subscription_id, resource_group_name=self.resource_group, workspace_name=self.name, session_id=session_id, filter = session_job_filter, orderby=orderby, skip=skip, top=top)

    def get_container_uri(
        self,
        job_id: Optional[str] = None,
        container_name: Optional[str] = None,
        container_name_format: Optional[str] = "job-{job_id}"
    ) -> str:
        """
        Get container URI based on job ID or container name.
        Creates a new container if it does not yet exist.

        :param job_id:
            Job ID, defaults to `None`.

        :param container_name:
            Container name, defaults to `None`.

        :param container_name_format:
            Container name format, defaults to "job-{job_id}".
        
        :return: Container URI.
        :rtype: str
        """
        if container_name is None:
            if job_id is not None:
                container_name = container_name_format.format(job_id=job_id)
            elif job_id is None:
                container_name = f"{self.name}-data"
        # Create container URI and get container client
        if self.storage is None:
            # Get linked storage account from the service, a new container
            # is created by the service if it does not yet exist
            container_uri = self._get_linked_storage_sas_uri(
                container_name
            )
        else:
            # Use the storage acount specified to generate container URI,
            # create a new container if it does not yet exist
            container_uri = get_container_uri(
                self.storage, container_name
            )
        return container_uri

    # def _create_filter(self,
    #         job_name: Optional[str] = None,
    #         item_type: Optional[List[str]] = None,
    #         job_type: Optional[List[str]] = None,
    #         provider_ids: Optional[List[str]] = None,
    #         target: Optional[List[str]] = None,
    #         status: Optional[List[str]] = None,
    #         created_after: Optional[datetime] = None,
    #         created_before: Optional[datetime] = None,) -> str:
    #     has_filter = False
    #     filter_string = ""

    #     if job_name:
    #         filter_string += f"startswith(Name, '{job_name}')"
    #         has_filter = True

    #     if (item_type is not None and len(item_type) != 0):
    #         if has_filter:
    #             filter_string += " and "

    #         filter_string += "("

    #         item_type_filter = " or ".join([f"ItemType eq '{iid}'" for iid in item_type])

    #         filter_string += f"{item_type_filter})"
    #         has_filter = True

    #     if (job_type is not None and len(job_type) != 0):
    #         if has_filter:
    #             filter_string += " and "

    #         filter_string += "("

    #         job_type_filter = " or ".join([f"JobType eq '{jid}'" for jid in job_type])

    #         filter_string += f"{job_type_filter})"
    #         has_filter = True

    #     if (provider_ids is not None and len(provider_ids) != 0):
    #         if has_filter:
    #             filter_string += " and "

    #         filter_string += "("

    #         provider_filter = " or ".join([f"ProviderId eq '{pid}'" for pid in provider_ids])

    #         filter_string += f"{provider_filter})"
    #         has_filter = True

    #     if (target is not None and len(target) != 0):
    #         if has_filter:
    #             filter_string += " and "

    #         filter_string += "("

    #         target_filter = " or ".join([f"Target eq '{tid}'" for tid in target])

    #         filter_string += f"{target_filter})"
    #         has_filter = True

    #     if (status is not None and len(status) != 0):
    #         if has_filter:
    #             filter_string += " and "

    #         filter_string += "("

    #         status_filter = " or ".join([f"State eq '{sid}'" for sid in status])

    #         filter_string += f"{status_filter})"
    #         has_filter = True

    #     if created_after is not None:
    #         if has_filter:
    #             filter_string += " and "

    #         iso_date_string = created_after.date().isoformat()
    #         filter_string += f"CreationTime ge {iso_date_string}"

    #     if created_before is not None:
    #         if has_filter:
    #             filter_string += " and "

    #         iso_date_string = created_before.date().isoformat()
    #         filter_string += f"CreationTime le {iso_date_string}"

    #     if filter_string:
    #         return filter_string
    #     else:
    #         return None

    # def _create_orderby(self, orderby_property: str, is_asc: bool) -> str:
    #     if orderby_property:
    #         var_names = ["Name", "ItemType", "JobType", "ProviderId", "Target", "State", "CreationTime"]

    #         if orderby_property in var_names:
    #             orderby = f"{orderby_property} asc" if is_asc else f"{orderby_property} desc"
    #         else:
    #             raise ValueError(f"Invalid orderby property: {orderby_property}")

    #         return orderby
    #     else:
    #         return None
    
    def close(self) -> None:
        self._mgmt_client.close()
        self._client.close()

    def __enter__(self) -> Self:
        self._client.__enter__()
        self._mgmt_client.__enter__()
        return self

    def __exit__(self, *exc_details: Any) -> None:
        self._mgmt_client.__exit__(*exc_details)
        self._client.__exit__(*exc_details)
