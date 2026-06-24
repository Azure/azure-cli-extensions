# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.azclierror import ArgumentUsageError


def validate_parameters(cmd, namespace):    # pylint: disable=unused-argument
    if not namespace.parameters:
        return

    from azext_horizondb.vendored_sdks.models import ParameterProperties

    parameter_list = []
    for item in namespace.parameters:
        if '=' not in item:
            raise ArgumentUsageError("Parameter '{}' must be in the format name=value.".format(item))
        name, value = item.split('=', 1)
        parameter_list.append(ParameterProperties(name=name, value=value))

    namespace.parameters = parameter_list
