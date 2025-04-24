from ._clients import MgmtApiClient
from knack.log import get_logger


class LocationDataHelper:

    _location_data = None
    _logger = None

    def __init__(self, cmd):
        self.cmd = cmd
        self._logger = get_logger(__name__)

    def get_location_data(self):
        if not LocationDataHelper._location_data:
            # query(cls, cmd, method, resource, api-version, requestBody):
            try:
                LocationDataHelper._location_data = MgmtApiClient.query(self,
                    self.cmd,
                    "GET",
                    "locations",
                    "2022-12-01",
                    None
                    )
            except Exception as e:
                self._logger.warning(
                            f"An error occurred while querying location data: {e}. No location data will be used."
                            "Please validate manually if the regions used support Availability Zones.")

        self._logger.debug(f"Loaded location data successfully.")

    def region_has_zones(region):
        if not LocationDataHelper._location_data:
            return None

        # While 'global' is not a valid region, we want to return true for global resources
        if region == 'global':
            return True

        if LocationDataHelper._location_data:
            for location in LocationDataHelper._location_data['value']:
                if location['name'].lower() == region.lower():
                    return 'availabilityZoneMappings' in location

        return None
