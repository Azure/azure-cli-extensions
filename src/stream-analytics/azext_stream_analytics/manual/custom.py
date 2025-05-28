# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

from azure.cli.core.azclierror import ArgumentUsageError


def stream_analytics_function_inspect(client,
                                      resource_group_name,
                                      job_name,
                                      function_name,
                                      azure_machine_learning_web_service_function_retrieve_default_definition_parameters=None):
    all_function_retrieve_default_definition_parameters = []
    if azure_machine_learning_web_service_function_retrieve_default_definition_parameters is not None:
        all_function_retrieve_default_definition_parameters.append(azure_machine_learning_web_service_function_retrieve_default_definition_parameters)
    if len(all_function_retrieve_default_definition_parameters) > 1:
        err_msg = "At most one {--ml-properties} is needed for function inspect."
        raise ArgumentUsageError(err_msg)
    function_retrieve_default_definition_parameters = all_function_retrieve_default_definition_parameters[0] if len(all_function_retrieve_default_definition_parameters) == 1 else None
    return client.retrieve_default_definition(resource_group_name=resource_group_name,
                                              job_name=job_name,
                                              function_name=function_name,
                                              function_retrieve_default_definition_parameters=function_retrieve_default_definition_parameters)
