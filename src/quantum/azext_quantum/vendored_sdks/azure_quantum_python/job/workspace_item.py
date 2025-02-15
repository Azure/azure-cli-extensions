##
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
##

import abc
from typing import TYPE_CHECKING, Union

# from azure.quantum._client.models import ItemDetails, ItemType, SessionDetails, JobDetails
from .._client.models import ItemDetails, ItemType, SessionDetails, JobDetails

if TYPE_CHECKING:
    # from azure.quantum.workspace import Workspace
    from ..workspace import Workspace

__all__ = ["WorkspaceItem"]


class WorkspaceItem(abc.ABC):
    """
    Workspace item base class.

    :param workspace: Workspace instance to submit job to
    :type workspace: Workspace
    :param details: Item details model,
            contains item ID, name and other details
    :type details: ItemDetails
    """

    def __init__(self, workspace: "Workspace", details: ItemDetails, **kwargs):
        self._workspace = workspace
        self._details = details
        self._item_type = details.item_type

    @property
    def workspace(self) -> "Workspace":
        """Workspace of the Workspace item"""
        return self._workspace

    @property
    def details(self) -> Union[SessionDetails, JobDetails]:
        """Workspace item details"""
        return self._details

    @property
    def id(self) -> str:
        """Id of the Workspace item"""
        return self._details.id

    @property
    def item_type(self) -> ItemType:
        """Workspace item type"""
        return self._item_type
