# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

from azure.cli.core.commands.parameters import resource_group_name_type

from azext_stream_analytics.action import AddAzureMachineLearningWebServiceFunctionRetrieveDefaultDefinitionParameters


def load_arguments(self, _):
    with self.argument_context("stream-analytics function inspect") as c:
        c.argument("resource_group_name", resource_group_name_type)
        c.argument("job_name", type=str, help="The name of the streaming job.")
        c.argument("function_name", options_list=["--name", "-n", "--function-name"], type=str,
                   help="The name of the function.")
        c.argument("azure_machine_learning_web_service_function_retrieve_default_definition_parameters",
                   options_list=["--ml-properties"],
                   action=AddAzureMachineLearningWebServiceFunctionRetrieveDefaultDefinitionParameters, nargs="+",
                   help="The parameters needed to retrieve the default function definition for an Azure Machine "
                   "Learning web service function.", arg_group="FunctionRetrieveDefaultDefinitionParameters")
