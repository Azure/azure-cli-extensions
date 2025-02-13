##
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
##

from typing import TYPE_CHECKING, Optional, Union, Protocol, List
from abc import abstractmethod

from azure.quantum._client.models import SessionDetails, SessionStatus, SessionJobFailurePolicy
from azure.quantum.job.workspace_item import WorkspaceItem
from azure.quantum.job import Job

__all__ = ["Session", "SessionHost", "SessionDetails", "SessionStatus", "SessionJobFailurePolicy"]

if TYPE_CHECKING:
    from azure.quantum.workspace import Workspace
    from azure.quantum.workspace import Target


class Session(WorkspaceItem):
    """Azure Quantum Job Session: a logical grouping of jobs.

    :param workspace: Workspace instance to open the session on
    :type workspace: Workspace

    :param details: Session details model, containing the session id,
                    name, job_failure_policy, provider_id and target.
                    Either this parameter should be passed containing all
                    the session detail values, or the same values should be
                    passed as individual parameters.
    :type details: Optional[SessionDetails]

    :param target: The name of the target (or Target object) to open the session on.
    :type target: Union[str, Target, None]

    :param provider_id: The id of the provider to open the session on.
                        If not passed, it will be extracted from the target name.
    :type provider_id: Optional[str]

    :param id: The id of the session. If not passed, one random uuid will used.
    :type id: Optional[str]

    :param name: The name of the session.
                 If not passed, the name will be `session-{session-id}`.
    :type name: Optional[str]

    :param job_failure_policy: The policy that determines when a session would fail,
                               close and not accept further jobs.
    :type job_failure_policy: Union[str, SessionJobFailurePolicy, None]

    :raises ValueError: if details is passed along individual parameters,
                        or if required parameters are missing.
    """

    def __init__(
            self,
            workspace: "Workspace",
            details: Optional[SessionDetails] = None,
            target: Union[str, "Target", None] = None,
            provider_id: Optional[str] = None,
            id: Optional[str] = None,
            name: Optional[str] = None,
            job_failure_policy: Union[str, SessionJobFailurePolicy, None] = None,
            **kwargs):
        from azure.quantum.target import Target
        target_name = target.name if isinstance(target, Target) else target
        self._target = target if isinstance(target, Target) else None

        if ((details is not None)
            and ((isinstance(target, str)) or
                 (provider_id is not None) or
                 (id is not None) or
                 (name is not None) or
                 (job_failure_policy is not None))):
            raise ValueError("""If `details` is passed, you should not pass `target`,
                                `provider_id`, `id`, `name` or `job_failure_policy`.""")

        if (details is None) and (target is None):
            raise ValueError("If `session_details` is not passed, you should at least pass the `target`.")

        if details is None:
            import uuid
            import re
            id = id if id is not None else str(uuid.uuid1())
            name = name if name is not None else f"session-{id}"
            if provider_id is None:
                match = re.match(r"(\w+)\.", target_name)
                if match is not None:
                    provider_id = match.group(1)
            details = SessionDetails(id=id,
                                     name=name,
                                     provider_id=provider_id,
                                     target=target_name,
                                     job_failure_policy=job_failure_policy,
                                     **kwargs)

        super().__init__(
            workspace=workspace,
            details=details,
            **kwargs
        )

    @property
    def details(self) -> SessionDetails:
        """Get the session details.

        :return: The details about the session.
        :rtype: SessionDetails
        """
        return self._details

    @details.setter
    def details(self, value: SessionDetails):
        """Set session details.
        
        :param value: The details about the session
        :type value: SessionDetails
        """
        self._details = value

    @property
    def target(self) -> "Target":
        """Get the target associated with the session.

        :return: The target associated with the session.
        :rtype: Target
        """
        return self._target

    def open(self) -> "Session":
        """Opens a session, effectively creating a new session in the
           Azure Quantum service, and allowing it to accept jobs under it.

        :return: The session object with updated details after its opening.
        :rtype: Session
        """
        self.workspace.open_session(self)
        return self

    def close(self) -> "Session":
        """Closes a session, not allowing further jobs to be submitted under
           the session.

        :return: The session object with updated details after its closing.
        :rtype: Session
        """
        self.workspace.close_session(self)
        return self

    def refresh(self) -> "Session":
        """Fetches the latest session details from the Azure Quantum service.

        :return: The session object with updated details.
        :rtype: Session
        """
        self.workspace.refresh_session(self)
        return self

    def list_jobs(self) -> List[Job]:
        """Lists all jobs associated with this session.

        :return: A list of all jobs associated with this session.
        :rtype: typing.List[Job]
        """
        return self.workspace.list_session_jobs(session_id=self.id)

    def is_in_terminal_state(self) -> bool:
        """Returns True if the session is in one of the possible
           terminal states(Succeeded, Failed and Timed_Out).

        :return: True if the session is in one of the terminal states.
        :rtype: bool
        """
        return (self.details.status == SessionStatus.SUCCEEDED
                or self.details.status == SessionStatus.FAILED
                or self.details.status == SessionStatus.TIMED_OUT)

    def __enter__(self):
        """PEP 343 context manager implementation to use a session in
           a `with` block.
           This `__enter__` method is a no-op.
        """
        return self

    def __exit__(self, type, value, traceback):
        """PEP 343 context manager implementation to use a session in
           a `with` block.
           This `__exit__` attempts to close the session.

        :raises Exception: re-raises the exception that was caught
                           in the `with` block.
        """
        self.close()
        if isinstance(value, Exception):
            raise


class SessionHost(Protocol):
    """A protocol to allow other objects to "host" a session.
    For example, a target object can host an open session and
    have all jobs that are being submitted through it to be associated
    with that session.

    Example (job 1 to 3 will be associated the session "MySession"):

    .. highlight:: python
    .. code-block::

       with target.open_session(name="MySession") as session:
            job1 = target.submit(input_data=input_data, job_name="Job 1")
            job2 = target.submit(input_data=input_data, job_name="Job 2")
            job3 = target.submit(input_data=input_data, job_name="Job 3")
    
    """

    _latest_session: Optional[Session] = None

    @property
    def latest_session(self) -> Optional[Session]:
        """Get the latest (open) session associated with this object.

        :return: The latest session object.
        :rtype: typing.Optional[Session]
        """
        return self._latest_session

    @latest_session.setter
    def latest_session(self, session: Optional[Session]):
        """Set the latest session.
        :param value: The latest session
        :type value: Optional[Session]
        """
        self._latest_session = session

    def get_latest_session_id(self) -> Optional[str]:
        """Get the latest (open) session id associated with this object.
           This id is used to associate jobs to the latest (open) session.

        :return: The latest session id.
        :rtype: typing.Optional[str]
        """
        return self.latest_session.id if self.latest_session else None

    @abstractmethod
    def _get_azure_workspace(self) -> "Workspace":
        raise NotImplementedError

    @abstractmethod
    def _get_azure_target_id(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def _get_azure_provider_id(self) -> str:
        raise NotImplementedError

    def open_session(
        self,
        details: Optional[SessionDetails] = None,
        id: Optional[str] = None,
        name: Optional[str] = None,
        job_failure_policy: Union[str, SessionJobFailurePolicy, None] = None,
        **kwargs
    ) -> Session:
        """Opens a session and associates all future job submissions to that
           session until the session is closed (which happens automatically
           after exiting a `with` block).

        Example (job 1 to 3 will be associated the session "MySession"):

        .. highlight:: python
        .. code-block::

           with target.open_session(name="MySession") as session:
                job1 = target.submit(input_data=input_data, job_name="Job 1")
                job2 = target.submit(input_data=input_data, job_name="Job 2")
                job3 = target.submit(input_data=input_data, job_name="Job 3")

        Note: If the session host (usually a `target` or qiskit `backend`)
        already has a session associated with it (in the `latest_session` property),
        then this method will first attempt to close that session before opening
        a new one.

        :param details: Session details model, containing the session id,
                        name, job_failure_policy, provider_id and target.
                        Either this parameter should be passed containing all
                        the session detail values, the same values should be
                        passed as individual parameters.

        :param id: The id of the session. If not passed, one random uuid will used.
        :type id: Optional[str]

        :param name: The name of the session.
                    If not passed, the name will be `session-{session-id}`.
        :type name: Optional[str]

        :param job_failure_policy: The policy that determines when a session would fail,
                                close and not accept further jobs.

        :return: The session object with updated details after its opening.
        :rtype: Session
        """
        if self.latest_session:
            self.latest_session.close()

        session = Session(details=details,
                          id=id,
                          name=name,
                          job_failure_policy=job_failure_policy,
                          workspace=self._get_azure_workspace(),
                          target=self._get_azure_target_id(),
                          provider_id=self._get_azure_provider_id(),
                          **kwargs)
        self.latest_session = session
        return session.open()
