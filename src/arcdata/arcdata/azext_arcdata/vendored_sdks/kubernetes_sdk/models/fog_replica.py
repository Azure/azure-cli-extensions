# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from azext_arcdata.vendored_sdks.kubernetes_sdk.models.dict_utils import SerializationUtils


class FogReplica(SerializationUtils):
    """
    Models the replica object in the failover group custom resource status
    Example:
    {
        "availabilityMode": "ASYNCHRONOUS_COMMIT",
        "connectedState": "CONNECTED",
        "healthState": "OK",
        "replicaName": "sql-dqwag",
        "role": "SECONDARY",
        "secondaryRoleAllowConnections": "ALL",
        "synchronizationState": "HEALTHY"
    }
    """

    def __init__(
        self,
        availabilityMode: str = None,
        connectedState: str = None,
        healthState: str = None,
        replicaName: str = None,
        role: str = None,
        secondaryRoleAllowConnections: str = None,
        synchronizationState: str = None,
    ):
        self._availabilityMode = availabilityMode
        self._connectedState = connectedState
        self._healthState = healthState
        self._replicaName = replicaName
        self._role = role
        self._secondaryRoleAllowConnections = secondaryRoleAllowConnections
        self._synchronizationState = synchronizationState

    @property
    def availabilityMode(self) -> str:
        """
        The availability mode of the replica
        """
        return self._availabilityMode

    @availabilityMode.setter
    def availabilityMode(self, am: str):
        self._availabilityMode = am

    @property
    def connectedState(self) -> str:
        """
        The connected state of the replica
        """
        return self._connectedState

    @connectedState.setter
    def connectedState(self, cs: str):
        self._connectedState = cs

    @property
    def healthState(self) -> str:
        """
        The health state of the replica
        """
        return self._healthState

    @healthState.setter
    def healthState(self, hs: str):
        self._healthState = hs

    @property
    def replicaName(self) -> str:
        """
        The name of the replica
        """
        return self._replicaName

    @replicaName.setter
    def replicaName(self, rn: str):
        self._replicaName = rn

    @property
    def role(self) -> str:
        """
        The role of the replica
        """
        return self._role

    @role.setter
    def role(self, r: str):
        self._role = r

    @property
    def secondaryRoleAllowConnections(self) -> str:
        """
        The secondary role allow connections of the replica
        """
        return self._secondaryRoleAllowConnections

    @secondaryRoleAllowConnections.setter
    def secondaryRoleAllowConnections(self, srac: str):
        self._secondaryRoleAllowConnections = srac

    @property
    def synchronizationState(self) -> str:
        """
        The synchronization state of the replica
        """
        return self._synchronizationState

    @synchronizationState.setter
    def synchronizationState(self, ss: str):
        self._synchronizationState = ss

    def _to_dict(self) -> dict:
        return {
            "availabilityMode": self._availabilityMode,
            "connectedState": self._connectedState,
            "healthState": self._healthState,
            "replicaName": self._replicaName,
            "role": self._role,
            "secondaryRoleAllowConnections": self._secondaryRoleAllowConnections,
            "synchronizationState": self._synchronizationState,
        }

    def _hydrate(self, d: dict):
        if "availabilityMode" in d:
            self.availabilityMode = d["availabilityMode"]
        if "connectedState" in d:
            self.connectedState = d["connectedState"]
        if "healthState" in d:
            self.healthState = d["healthState"]
        if "replicaName" in d:
            self.replicaName = d["replicaName"]
        if "role" in d:
            self.role = d["role"]
        if "secondaryRoleAllowConnections" in d:
            self.secondaryRoleAllowConnections = d[
                "secondaryRoleAllowConnections"
            ]
        if "synchronizationState" in d:
            self.synchronizationState = d["synchronizationState"]
