# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

import argparse

from collections import defaultdict
from azure.cli.core.azclierror import ArgumentUsageError


class AddAzureMachineLearningWebServiceFunctionRetrieveDefaultDefinitionParameters(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        namespace.azure_machine_learning_web_service_function_retrieve_default_definition_parameters = action

    @staticmethod
    def get_action(values, option_string):
        try:
            properties = defaultdict(list)
            for (k, v) in (x.split('=', 1) for x in values):
                properties[k].append(v)
            properties = dict(properties)
        except Exception as error:
            err_msg = f"The content of {option_string} should be like [KEY=VALUE ...]."
            raise ArgumentUsageError(err_msg) from error
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == "execute-endpoint":
                d["execute_endpoint"] = v[0]
            else:
                err_msg = f"Unsupported Key {k} is provided for {option_string}. All possible keys are: script."
                raise ArgumentUsageError(err_msg)
        d["udf_type"] = "Scalar"
        d["binding_type"] = "Microsoft.MachineLearning/WebService"
        return d
