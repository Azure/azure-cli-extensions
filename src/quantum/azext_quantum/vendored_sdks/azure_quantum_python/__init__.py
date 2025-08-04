##
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
##

"""Defines interfaces for interacting with Azure Quantum"""


import logging
from .version import __version__

# from .job.job import *
# from .job.session import *
from .workspace import *

from ._client.models._enums import JobStatus, SessionStatus, SessionJobFailurePolicy, ItemType

logger = logging.getLogger(__name__)
logger.info(f"version: {__version__}")


__all__ = [ "Workspace" ]