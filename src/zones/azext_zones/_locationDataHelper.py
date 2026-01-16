# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._clients import MgmtApiClient
from knack.log import get_logger


class LocationDataHelper:

    _location_data = None
    _logger = None

    def __init__(self, cmd):
        self.cmd = cmd
        self._logger = get_logger(__name__)

    def fetch_location_data(self):
        if not LocationDataHelper._location_data:
            # query(cls, cmd, method, resource, api-version, requestBody):
            LocationDataHelper._location_data = MgmtApiClient.query(self,
                                                                    self.cmd,
                                                                    "GET",
                                                                    "locations",
                                                                    "2022-12-01",
                                                                    None
                                                                    )

        self._logger.debug("Loaded location data successfully.")

    def region_has_zones(self, region):
        if LocationDataHelper._location_data is None:
            return None

        # While 'global' is not a valid region, we want to return true for global resources
        if region == 'global':
            return True

        if LocationDataHelper._location_data:
            location_data = LocationDataHelper._location_data.get('value', [])
            for location in location_data:
                if location['name'].lower() == region.lower():
                    return 'availabilityZoneMappings' in location

        return None
