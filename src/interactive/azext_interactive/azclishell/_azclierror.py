# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.azclierror import ClientRequestError


# pylint: disable=unnecessary-pass
class ScenarioSearchError(ClientRequestError):
    """ The client error raised by `Scenario Search`. """
    pass
