# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger
from ._resourceTypeValidation import ResourceTypeValidatorFactory, ZoneRedundancyValidationResult
from ._argHelper import build_arg_query, execute_arg_query
from ._locationHelper import LocationDataHelper

__logger = get_logger(__name__)


def validate_zones(client, cmd, resource_group_names):

    # Get the location data we'll use to validate the resources
    location_data_helper = LocationDataHelper(cmd)
    location_data = location_data_helper.get_location_data()

    # Build the ARG query to retrieve resources
    query = build_arg_query(resource_group_names, None)
    __logger.debug("Built ARG Query: %s", query)

    # Retrieve the list of resources to validate
    resources = execute_arg_query(client, query, None, 0, None, None, False, None)

    # Run validation on the retrieved resources
    validation_results = validate_resources(resources)

    # Present the results to the user
    return validation_results

    if(cmd.output == 'table'):
        # Output results in table format
        from knack.table import TableFormatter
        from knack.output import table_output       

        table = TableFormatter(cmd, cmd.output).get_table()
        table_output(cmd, table, validation_results)

    # Default to json output if no specific format is requested
    return validation_results


def validate_resources(resources):
    resource_results = []
    if resources['count'] == 0:
        errMsg = ("No resources found, validation could not be run.")
        __logger.error(errMsg)

    # Loop through the resources and validate each one
    for resource in resources['data']:
        resourceProvider = resource['type'].split('/')[0]
        region = resource['location']  
        zrStatus = None                

        # If the region does not have zones, we need to look no further
        regionHasZones = LocationDataHelper.region_has_zones(region)
        if(regionHasZones is False):
            zrStatus = ZoneRedundancyValidationResult.NoZonesInRegion
        else:
            validator = ResourceTypeValidatorFactory.getValidator(resourceProvider)
            zrStatus = ZoneRedundancyValidationResult.Unknown if validator is None else validator.validate(resource)

        resource_result = {}
        resource_result['name'] = resource['name']
        resource_result['location'] = resource['location']
        resource_result['resourceGroup'] = resource['resourceGroup']
        resource_result['resourceType'] =  resource['type']
        resource_result['zoneRedundant'] = ZoneRedundancyValidationResult.to_string(zrStatus)
        resource_results.append(resource_result)

    return resource_results
