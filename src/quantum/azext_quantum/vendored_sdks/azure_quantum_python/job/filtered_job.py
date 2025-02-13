##
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
##
import re
import abc

from typing import Optional
from datetime import date, datetime, timezone

from azure.quantum._client.models import JobStatus


class FilteredJob(abc.ABC):
    """
    Mixin for adding methods to filter jobs
    """
    def matches_filter(
        self, 
        name_match: str = None, 
        status:  Optional[JobStatus] = None,
        created_after: Optional[datetime] = None
    ) -> bool:
        """Checks if job (self) matches the given properties if any.

            :param name_match: regex expression for job name matching
            :type name_match: str
            :param status: filter by job status
            :type status: Optional[JobStatus]
            :param created_after: filter jobs after time of job creation
            :type status: Optional[datetime]
            :return: Is filter match
            :rtype: bool
        """
        if name_match is not None and re.search(name_match, self.details.name) is None:
           return False
        
        if status is not None and self.details.status != status.value:
            return False
        
        if created_after is not None:
            # if supplied date is date we must convert to datetime first
            if isinstance(created_after, date):
                created_after = datetime(created_after.year, created_after.month, created_after.day)
            
            # if supplied date is naive, assume local and convert to timezone aware object
            if created_after.tzinfo is None:
                created_after = created_after.astimezone()
            
            if self.details.creation_time.replace(tzinfo=timezone.utc) < created_after:
                return False

        return True
