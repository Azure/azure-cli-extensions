##
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
##
from __future__ import annotations
import re
import os
from re import Match
from typing import (
    Optional,
    Callable,
    Union,
    Any
)
from azure.core.credentials import AzureKeyCredential
from azure.core.pipeline.policies import AzureKeyCredentialPolicy
# from azure.quantum._authentication import _DefaultAzureCredential
from ._authentication import _DefaultAzureCredential
# from azure.quantum._constants import (
from ._constants import (
    EnvironmentKind,
    EnvironmentVariables,
    ConnectionConstants,
    GUID_REGEX_PATTERN,
)

class WorkspaceConnectionParams:
    """
    Internal Azure Quantum Python SDK class to handle logic
    for the parameters needed to connect to a Workspace.
    """

    RESOURCE_ID_REGEX = re.compile(
        fr"""
            ^
            /subscriptions/(?P<subscription_id>{GUID_REGEX_PATTERN})
            /resourceGroups/(?P<resource_group>[^\s/]+)
            /providers/Microsoft\.Quantum
            /Workspaces/(?P<workspace_name>[^\s/]+)
            $
        """,
        re.VERBOSE | re.IGNORECASE)

    CONNECTION_STRING_REGEX = re.compile(
        fr"""
            ^
            SubscriptionId=(?P<subscription_id>{GUID_REGEX_PATTERN});
            ResourceGroupName=(?P<resource_group>[^\s;]+);
            WorkspaceName=(?P<workspace_name>[^\s;]+);
            ApiKey=(?P<api_key>[^\s;]+);
            QuantumEndpoint=(?P<quantum_endpoint>https://(?P<location>[^\s\.]+).quantum(?:-test)?.azure.com/);
        """,
        re.VERBOSE | re.IGNORECASE)

    def __init__(
        self,
        subscription_id: Optional[str] = None,
        resource_group: Optional[str] = None,
        workspace_name: Optional[str] = None,
        location: Optional[str] = None,
        quantum_endpoint: Optional[str] = None,
        arm_endpoint: Optional[str] = None,
        environment: Union[str, EnvironmentKind, None] = None,
        credential: Optional[object] = None,
        resource_id: Optional[str] = None,
        user_agent: Optional[str] = None,
        user_agent_app_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        api_version: Optional[str] = None,
        connection_string: Optional[str] = None,
        on_new_client_request: Optional[Callable] = None,
    ):
        # fields are used for these properties since
        # they have special getters/setters
        self._location = None
        self._environment = None
        self._quantum_endpoint = None
        self._arm_endpoint = None
        # regular connection properties
        self.subscription_id = None
        self.resource_group = None
        self.workspace_name = None
        self.credential = None
        self.user_agent = None
        self.user_agent_app_id = None
        self.client_id = None
        self.tenant_id = None
        self.api_version = None
        # callback to create a new client if needed
        # for example, when changing the user agent
        self.on_new_client_request = on_new_client_request
        # merge the connection parameters passed
        # connection_string is set first as it
        # should be overridden by other parameters
        self.apply_connection_string(connection_string)
        self.merge(
            api_version=api_version,
            arm_endpoint=arm_endpoint,
            quantum_endpoint=quantum_endpoint,
            client_id=client_id,
            credential=credential,
            environment=environment,
            location=location,
            resource_group=resource_group,
            subscription_id=subscription_id,
            tenant_id=tenant_id,
            user_agent=user_agent,
            user_agent_app_id=user_agent_app_id,
            workspace_name=workspace_name,
        )
        self.apply_resource_id(resource_id=resource_id)

    @property
    def location(self):
        """
        The Azure location.
        On the setter, we normalize the value removing spaces
        and converting it to lowercase.
        """
        return self._location

    @location.setter
    def location(self, value: str):
        self._location = (value.replace(" ", "").lower()
                          if isinstance(value, str)
                          else value)

    @property
    def environment(self):
        """
        The environment kind, such as dogfood, canary or production.
        Defaults to EnvironmentKind.PRODUCTION
        """
        return self._environment or EnvironmentKind.PRODUCTION

    @environment.setter
    def environment(self, value: Union[str, EnvironmentKind]):
        self._environment = (EnvironmentKind[value.upper()]
                             if isinstance(value, str)
                             else value)

    @property
    def quantum_endpoint(self):
        """
        The Azure Quantum data plane endpoint.
        Defaults to well-known endpoint based on the environment.
        """
        if self._quantum_endpoint:
            return self._quantum_endpoint
        if not self.location:
            raise ValueError("Location not specified")
        if self.environment is EnvironmentKind.PRODUCTION:
            return ConnectionConstants.GET_QUANTUM_PRODUCTION_ENDPOINT(self.location)
        if self.environment is EnvironmentKind.CANARY:
            return ConnectionConstants.GET_QUANTUM_CANARY_ENDPOINT(self.location)
        if self.environment is EnvironmentKind.DOGFOOD:
            return ConnectionConstants.GET_QUANTUM_DOGFOOD_ENDPOINT(self.location)
        raise ValueError(f"Unknown environment `{self.environment}`.")

    @quantum_endpoint.setter
    def quantum_endpoint(self, value: str):
        self._quantum_endpoint = value

    @property
    def arm_endpoint(self):
        """
        The control plane endpoint.
        Defaults to well-known arm_endpoint based on the environment.
        """
        if self._arm_endpoint:
            return self._arm_endpoint
        if self.environment is EnvironmentKind.DOGFOOD:
            return ConnectionConstants.ARM_DOGFOOD_ENDPOINT
        if self.environment in [EnvironmentKind.PRODUCTION,
                                EnvironmentKind.CANARY]:
            return ConnectionConstants.ARM_PRODUCTION_ENDPOINT
        raise ValueError(f"Unknown environment `{self.environment}`.")

    @arm_endpoint.setter
    def arm_endpoint(self, value: str):
        self._arm_endpoint = value

    @property
    def api_key(self):
        """
        The api-key stored in a AzureKeyCredential.
        """
        return (self.credential.key
                if isinstance(self.credential, AzureKeyCredential)
                else None)

    @api_key.setter
    def api_key(self, value: str):
        if value:
            self.credential = AzureKeyCredential(value)
        self._api_key = value

    def __repr__(self):
        """
        Print all fields and properties.
        """
        info = []
        for key in vars(self):
            info.append(f"    {key}: {self.__dict__[key]}")
        cls = type(self)
        for key in dir(self):
            attr = getattr(cls, key, None)
            if attr and isinstance(attr, property) and attr.fget:
                info.append(f"    {key}: {attr.fget(self)}")
        info.sort()
        info.insert(0, super().__repr__())
        return "\n".join(info)

    def apply_resource_id(self, resource_id: str):
        """
        Parses the resource_id and set the connection
        parameters obtained from it.
        """
        if resource_id:
            match = re.search(
                WorkspaceConnectionParams.RESOURCE_ID_REGEX,
                resource_id)
            if not match:
                raise ValueError("Invalid resource id")
            self._merge_re_match(match)

    def apply_connection_string(self, connection_string: str):
        """
        Parses the connection_string and set the connection
        parameters obtained from it.
        """
        if connection_string:
            match = re.search(
                WorkspaceConnectionParams.CONNECTION_STRING_REGEX,
                connection_string)
            if not match:
                raise ValueError("Invalid connection string")
            self._merge_re_match(match)

    def merge(
        self,
        subscription_id: Optional[str] = None,
        resource_group: Optional[str] = None,
        workspace_name: Optional[str] = None,
        location: Optional[str] = None,
        quantum_endpoint: Optional[str] = None,
        arm_endpoint: Optional[str] = None,
        environment: Union[str, EnvironmentKind, None] = None,
        credential: Optional[object] = None,
        user_agent: Optional[str] = None,
        user_agent_app_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        api_version: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """
        Set all fields/properties with `not None` values
        passed in the (named or key-valued) arguments
        into this instance.
        """
        self._merge(
            api_version=api_version,
            arm_endpoint=arm_endpoint,
            quantum_endpoint=quantum_endpoint,
            client_id=client_id,
            credential=credential,
            environment=environment,
            location=location,
            resource_group=resource_group,
            subscription_id=subscription_id,
            tenant_id=tenant_id,
            user_agent=user_agent,
            user_agent_app_id=user_agent_app_id,
            workspace_name=workspace_name,
            api_key=api_key,
            merge_default_mode=False,
        )
        return self

    def apply_defaults(
        self,
        subscription_id: Optional[str] = None,
        resource_group: Optional[str] = None,
        workspace_name: Optional[str] = None,
        location: Optional[str] = None,
        quantum_endpoint: Optional[str] = None,
        arm_endpoint: Optional[str] = None,
        environment: Union[str, EnvironmentKind, None] = None,
        credential: Optional[object] = None,
        user_agent: Optional[str] = None,
        user_agent_app_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        api_version: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> WorkspaceConnectionParams:
        """
        Set all fields/properties with `not None` values
        passed in the (named or key-valued) arguments
        into this instance IF the instance does not have
        the corresponding parameter set yet.
        """
        self._merge(
            api_version=api_version,
            arm_endpoint=arm_endpoint,
            quantum_endpoint=quantum_endpoint,
            client_id=client_id,
            credential=credential,
            environment=environment,
            location=location,
            resource_group=resource_group,
            subscription_id=subscription_id,
            tenant_id=tenant_id,
            user_agent=user_agent,
            user_agent_app_id=user_agent_app_id,
            workspace_name=workspace_name,
            api_key=api_key,
            merge_default_mode=True,
        )
        return self

    def _merge(
        self,
        merge_default_mode: bool,
        subscription_id: Optional[str] = None,
        resource_group: Optional[str] = None,
        workspace_name: Optional[str] = None,
        location: Optional[str] = None,
        quantum_endpoint: Optional[str] = None,
        arm_endpoint: Optional[str] = None,
        environment: Union[str, EnvironmentKind, None] = None,
        credential: Optional[object] = None,
        user_agent: Optional[str] = None,
        user_agent_app_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        api_version: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """
        Set all fields/properties with `not None` values
        passed in the kwargs arguments
        into this instance.

        If merge_default_mode is True, skip setting
        the field/property if it already has a value.
        """
        def _get_value_or_default(old_value, new_value):
            if merge_default_mode and old_value:
                return old_value
            if new_value:
                return new_value
            return old_value

        self.subscription_id = _get_value_or_default(self.subscription_id, subscription_id)
        self.resource_group = _get_value_or_default(self.resource_group, resource_group)
        self.workspace_name = _get_value_or_default(self.workspace_name, workspace_name)
        self.location = _get_value_or_default(self.location, location)
        self.environment = _get_value_or_default(self.environment, environment)
        self.credential = _get_value_or_default(self.credential, credential)
        self.user_agent = _get_value_or_default(self.user_agent, user_agent)
        self.user_agent_app_id = _get_value_or_default(self.user_agent_app_id, user_agent_app_id)
        self.client_id = _get_value_or_default(self.client_id, client_id)
        self.tenant_id = _get_value_or_default(self.tenant_id, tenant_id)
        self.api_version = _get_value_or_default(self.api_version, api_version)
        self.api_key = _get_value_or_default(self.api_key, api_key)
        # for these properties that have a default value in the getter, we use
        # the private field as the old_value
        self.quantum_endpoint = _get_value_or_default(self._quantum_endpoint, quantum_endpoint)
        self.arm_endpoint = _get_value_or_default(self._arm_endpoint, arm_endpoint)
        return self

    def _merge_connection_params(
        self,
        connection_params: WorkspaceConnectionParams,
        merge_default_mode: bool = False,
    ) -> WorkspaceConnectionParams:
        """
        Set all fields/properties with `not None` values
        from the `connection_params` into this instance.
        """
        self._merge(
            api_version=connection_params.api_version,
            client_id=connection_params.client_id,
            credential=connection_params.credential,
            environment=connection_params.environment,
            location=connection_params.location,
            resource_group=connection_params.resource_group,
            subscription_id=connection_params.subscription_id,
            tenant_id=connection_params.tenant_id,
            user_agent=connection_params.user_agent,
            user_agent_app_id=connection_params.user_agent_app_id,
            workspace_name=connection_params.workspace_name,
            merge_default_mode=merge_default_mode,
            # for these properties that have a default value in the getter,
            # so we use the private field instead
            # pylint: disable=protected-access
            arm_endpoint=connection_params._arm_endpoint,
            quantum_endpoint=connection_params._quantum_endpoint,
        )
        return self

    def get_credential_or_default(self) -> Any:
        """
        Get the credential if one was set,
        or defaults to a new _DefaultAzureCredential.
        """
        return (self.credential
                or _DefaultAzureCredential(
                    subscription_id=self.subscription_id,
                    arm_endpoint=self.arm_endpoint,
                    tenant_id=self.tenant_id))

    def get_auth_policy(self) -> Any:
        """
        Returns a AzureKeyCredentialPolicy if using an AzureKeyCredential.
        Defaults to None.
        """
        if isinstance(self.credential, AzureKeyCredential):
            return AzureKeyCredentialPolicy(self.credential,
                                            ConnectionConstants.QUANTUM_API_KEY_HEADER)
        return None

    def append_user_agent(self, value: str):
        """
        Append a new value to the Workspace's UserAgent and re-initialize the
        QuantumClient. The values are appended using a dash.

        :param value: UserAgent value to add, e.g. "azure-quantum-<plugin>"
        """
        new_user_agent = None

        if (
            value
            and value not in (self.user_agent or "")
        ):
            new_user_agent = (f"{self.user_agent}-{value}"
                              if self.user_agent else value)

        if new_user_agent != self.user_agent:
            self.user_agent = new_user_agent
            if self.on_new_client_request:
                self.on_new_client_request()

    def get_full_user_agent(self):
        """
        Get the full Azure Quantum Python SDK UserAgent
        that is sent to the service via the header.
        """
        full_user_agent = self.user_agent
        app_id = self.user_agent_app_id
        if self.user_agent_app_id:
            full_user_agent = (f"{app_id} {full_user_agent}"
                               if full_user_agent else app_id)
        return full_user_agent

    def is_complete(self) -> bool:
        """
        Returns true if we have all necessary parameters
        to connect to the Azure Quantum Workspace.
        """
        return (self.location
                and self.subscription_id
                and self.resource_group
                and self.workspace_name
                and self.get_credential_or_default())

    def assert_complete(self):
        """
        Raises ValueError if we don't have all necessary parameters
        to connect to the Azure Quantum Workspace.
        """
        if not self.is_complete():
            raise ValueError(
                """
                    Azure Quantum workspace not fully specified.
                    Please specify one of the following:
                    1) A valid combination of location and resource ID.
                    2) A valid combination of location, subscription ID,
                    resource group name, and workspace name.
                    3) A valid connection string (via Workspace.from_connection_string()).
                """)

    def default_from_env_vars(self) -> WorkspaceConnectionParams:
        """
        Apply default values found in the environment variables
        if current parameters are not set.
        """
        self.subscription_id = (self.subscription_id
                                or os.environ.get(EnvironmentVariables.QUANTUM_SUBSCRIPTION_ID)
                                or os.environ.get(EnvironmentVariables.SUBSCRIPTION_ID))
        self.resource_group = (self.resource_group
                               or os.environ.get(EnvironmentVariables.QUANTUM_RESOURCE_GROUP)
                               or os.environ.get(EnvironmentVariables.RESOURCE_GROUP))
        self.workspace_name = (self.workspace_name
                               or os.environ.get(EnvironmentVariables.WORKSPACE_NAME))
        self.location = (self.location
                         or os.environ.get(EnvironmentVariables.QUANTUM_LOCATION)
                         or os.environ.get(EnvironmentVariables.LOCATION))
        self.user_agent_app_id = (self.user_agent_app_id
                                  or os.environ.get(EnvironmentVariables.USER_AGENT_APPID))
        self.tenant_id = (self.tenant_id
                          or os.environ.get(EnvironmentVariables.AZURE_TENANT_ID))
        self.client_id = (self.client_id
                          or os.environ.get(EnvironmentVariables.AZURE_CLIENT_ID))
        # for these properties we use the private field
        # because the getter return default values
        self.environment = (self._environment
                            or os.environ.get(EnvironmentVariables.QUANTUM_ENV))
        # only try to use the connection string from env var if
        # we really need it
        if (not self.location
            or not self.subscription_id
            or not self.resource_group
            or not self.workspace_name
            or not self.credential
        ):
            self._merge_connection_params(
                connection_params=WorkspaceConnectionParams(
                    connection_string=os.environ.get(EnvironmentVariables.CONNECTION_STRING)),
                merge_default_mode=True)
        return self

    @classmethod
    def from_env_vars(
        cls,
    ) -> WorkspaceConnectionParams:
        """
        Initialize the WorkspaceConnectionParams from values found
        in the environment variables.
        """
        return WorkspaceConnectionParams().default_from_env_vars()

    def _merge_re_match(self, re_match: Match[str]):
        def get_value(group_name):
            return re_match.groupdict().get(group_name)
        self.merge(
            subscription_id=get_value('subscription_id'),
            resource_group=get_value('resource_group'),
            workspace_name=get_value('workspace_name'),
            location=get_value('location'),
            quantum_endpoint=get_value('quantum_endpoint'),
            api_key=get_value('api_key'),
            arm_endpoint=get_value('arm_endpoint'),
        )
