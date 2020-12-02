# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.azclierror import InvalidArgumentValueError


def validate_configuration_type(configuration_type):
    if configuration_type.lower() != 'sourcecontrolconfiguration':
        raise InvalidArgumentValueError(
            'Invalid configuration-type',
            'Try specifying the valid value "sourceControlConfiguration"')
