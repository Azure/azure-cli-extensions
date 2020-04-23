# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError


def validate_configuration_type(configuration_type):
    if configuration_type.lower() != 'sourcecontrolconfiguration':
        raise CLIError('Invalid configuration-type.  Valid value is "sourceControlConfiguration"')
