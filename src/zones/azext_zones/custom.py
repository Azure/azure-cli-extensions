# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger
from .resourceTypeValidation import ResourceTypeValidatorFactory, ZoneRedundancyValidationResult
from ._argHelper import build_arg_query, execute_arg_query

__logger = get_logger(__name__)


def validate_zones(client, cmd, resource_group_names):
    # Build the ARG query to retrieve resources
    query = build_arg_query(resource_group_names, None, None)
    __logger.warning("Query: %s", query)

    # Retrieve the list of resources to validate
    resources = execute_arg_query(client, query, 100, 0, None, None, False, None)

    # Run validation on the retrieved resources
    validation_results = validate_resources(resources)

    # Present the results to the user
    return validation_results

    if(cmd.output == 'table'):
        # Output results in table format
        from knack.table import TableFormatter
        from knack.output import table_output       

        table = TableFormatter(cmd, cmd.output).get_table()
        table.add_column('Name', 'name')    
        table.add_column('Location', 'location')
        table.add_column('Resource Group', 'resourceGroup')
        table.add_column('Type', 'type')
        table.add_column('Zone Redundant', 'zoneRedundant')
        table.add_row(validation_results)
        table_output(cmd, table, validation_results)

    return validation_results


def validate_resources(resources):
    resource_results = []
    if resources['count'] == 0:
        errMsg = ("No resources found, validation could not be run.")
        __logger.error(errMsg)

    # Loop through the resources and validate each one
    for resource in resources['data']:
        resourceProvider = resource['type'].split('/')[0]
        validator = ResourceTypeValidatorFactory.getValidator(resourceProvider)
        zrStatus = ZoneRedundancyValidationResult.Unknown if validator is None else validator.validate(resource)
        resource_result = {}
        resource_result['name'] = resource['name']
        resource_result['location'] = resource['location']
        resource_result['resourceGroup'] = resource['resourceGroup']
        resource_result['type'] = resource['type']
        resource_result['zoneRedundant'] = ZoneRedundancyValidationResult.to_string(zrStatus)
        resource_results.append(resource_result)

    return resource_results
