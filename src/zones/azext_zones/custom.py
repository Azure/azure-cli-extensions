# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger
from ._resourceTypeValidation import getResourceTypeValidator, ZoneRedundancyValidationResult
from ._argHelper import build_arg_query, execute_arg_query
from ._locationDataHelper import LocationDataHelper

__logger = get_logger(__name__)


def validate_zones(client, cmd, omit_dependent, resource_group_names, tags):
    # Build the ARG query to retrieve resources
    query = build_arg_query(resource_group_names, tags)
    __logger.debug("Built ARG Query: %s", query)

    # Retrieve the list of resources to validate
    resources = execute_arg_query(client, query, None, 0, None, None, False, None)

    # Run validation on the retrieved resources
    validation_results = validate_resources(cmd, resources, omit_dependent)

    return validation_results


def validate_resources(cmd, resources, omit_dependent=False):
    resource_results = []
    if resources['count'] == 0:
        errMsg = ("No resources found with the supplied resource group and tag filters, validation could not be run.")
        __logger.error(errMsg)

    # Get the location data we'll use to validate the resources
    try:
        location_data_helper = LocationDataHelper(cmd)
        location_data_helper.fetch_location_data()
    except Exception as e:  # pylint: disable=broad-except
        __logger.debug("An error occurred when fetching location data: %s", e)
        __logger.warning("An error occurred when fetching location data. \
                        Please manually validate if your region supports zones.")

    # Loop through the resources and validate each one
    for resource in resources['data']:
        resourceProvider = resource['type'].split('/')[0]
        region = resource['location']
        zrStatus = None

        # If the region does not have zones, we need to look no further
        # If we were unable to fetch location data before, this will return None and it will fall into the else logic
        regionHasZones = location_data_helper.region_has_zones(region)
        if not regionHasZones:
            zrStatus = ZoneRedundancyValidationResult.NoZonesInRegion
        else:
            validator = getResourceTypeValidator(resourceProvider)
            if validator is None:
                zrStatus = ZoneRedundancyValidationResult.Unknown
            else:
                try:
                    zrStatus = validator.validate(resource)
                except KeyError as e:
                    __logger.warning("KeyError when validating %s: %s\n \
                                    Please check the resource manually.", resource.get('name', ''), e)
                    zrStatus = ZoneRedundancyValidationResult.Unknown
                except Exception as e:  # pylint: disable=broad-except
                    __logger.warning("An error occurred when validating %s: %s\n \
                                    Please check the resource manually.", resource.get('name', ''), e)
                    zrStatus = ZoneRedundancyValidationResult.Unknown

        if zrStatus is not ZoneRedundancyValidationResult.Dependent or not omit_dependent:
            resource_result = {}
            resource_result['name'] = resource['name']
            resource_result['location'] = resource['location']
            resource_result['resourceGroup'] = resource['resourceGroup']
            resource_result['resourceType'] = resource['type']
            resource_result['zoneRedundant'] = ZoneRedundancyValidationResult.to_string(zrStatus)
            resource_results.append(resource_result)

    return resource_results
