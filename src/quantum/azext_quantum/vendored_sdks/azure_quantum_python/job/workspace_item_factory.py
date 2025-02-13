##
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
##

from typing import TYPE_CHECKING, Union

from azure.quantum._client.models import SessionDetails, JobDetails
from azure.quantum.job.job import Job
from azure.quantum.job.session import Session

if TYPE_CHECKING:
    from azure.quantum.workspace import Workspace

__all__ = ["WorkspaceItemFactory"]

class WorkspaceItemFactory():
    """

    :param workspace: Workspace instance to submit job to
    :type workspace: Workspace
    :param item_details: Item details model,
            contains item ID, name and other details
    :type item_details: ItemDetails
    """

    @staticmethod
    def __new__(workspace:"Workspace",
                item_details:Union[SessionDetails, JobDetails]
               ) -> Union[Session, Job]:
        if isinstance(item_details, JobDetails):
            return Job(workspace, job_details=item_details)
        elif isinstance(item_details, SessionDetails):
            return Session(workspace, details=item_details)
        else:
            raise TypeError("item_details must be of type `SessionDetails` or `JobDetails`.")
