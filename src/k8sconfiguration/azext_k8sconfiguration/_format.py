# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from collections import OrderedDict


def k8sconfiguration_list_table_format(results):
    formatted_result = []
    for result in results:
        formatted_result.append(
            OrderedDict([
                ('name', result['name']),
                ('repositoryUrl', result['repositoryUrl']),
                ('operatorName', result['operatorInstanceName']),
                ('operatorNamespace', result['operatorNamespace']),
                ('scope', result['operatorScope']),
                ('provisioningState', result['provisioningState'])
            ])
        )
    return formatted_result


def k8sconfiguration_show_table_format(result):
    return OrderedDict([
        ('name', result['name']),
        ('repositoryUrl', result['repositoryUrl']),
        ('operatorName', result['operatorInstanceName']),
        ('operatorNamespace', result['operatorNamespace']),
        ('scope', result['operatorScope']),
        ('provisioningState', result['provisioningState'])
    ])
